# describes tiling of multiple loops.
# FIXME figure out what the best way of calling SysTL functions here is.
# probably need an import or two.

from __future__ import annotations
import sys
from SYS_ATL import proc, Procedure, DRAM, config, instr, QAST
from MoST.MoST_base import *
from MoST.qast_utils.loopReader import *
from itertools import dropwhile

class TilingSchedule(MoSTSchedule):
    #loop bounds are a ForLoop object
    #tile_bounds is a dict mapping names from the ForLoop to numbers
    def __init__(self, loop_bounds, tile_bounds, simplify=True):
        self.loop_bounds = loop_bounds
        self.tile_bounds = tile_bounds
        self.simplify = simplify

    def apply(self, fn, backend="systl"):
        for loop in self.loop_bounds:
            block_size = self.tile_bounds[loop.name]
            new_names = (loop.name + "_out", loop.name + "_in")
            perfect = False #FIXME detect if lo, hi are constant; can infer
            fn = fn.split(loop.name + " #0", block_size, new_names,
              tail='cut', perfect=perfect)
            new_bounds = getNestBounds(fn)
            loop_indices = [loop.name for loop in new_bounds]
            _, *indices_after = dropwhile(lambda idx: idx != loop.name + '_in', loop_indices)
            for idxafter in indices_after:
                fn = fn.reorder(loop.name + "_in #0", idxafter)
        if self.simplify:
            fn = fn.simplify()
        return fn

    # generates tiles for projective nested loops
    # see https://arxiv.org/abs/2003.00119
    # but this also includes ability to determine optimal alloc
    # thanks to Riley Murray for the code to do this
    @classmethod
    def generateHBLProjectiveTile(cls, bounds, accesses, memsize, verbose=False):
        import numpy as np
        import cvxpy as cp

        def make_model(ell, phis, M):
            """
            ell : a numpy ndarray.
            phis : list. phi[j] is a list (or numpy ndarray) containing some integers from range(n)
            M : real numeric type
            """
            n = ell.size
            m = len(phis)
            ell[ell == np.inf] = M
            # optimization variable
            b = cp.Variable(shape=(n,), name='b', pos=True)
            # constraints
            summands = [cp.prod(b[phis[j]]) for j in range(m)]
            constraints = [cp.sum(summands) <= M, b <= ell]
            # objective function
            objective = cp.Maximize(cp.prod(b))
            # Problem object
            prob = cp.Problem(objective, constraints)
            return prob

        varidx = dict([(bounds[i].name, i) for i in range(len(bounds))])
        idxvar = dict([(i, bounds[i].name) for i in range(len(bounds))])
        loophi = [loop.hi for loop in bounds]
        looplo = [loop.lo for loop in bounds]
        if not all(map(lambda bound: isinstance(bound, QAST.Const), loophi)):
            raise NotImplementedError("Can't specialize for nonconst bounds")
        if not all(map(lambda bound: isinstance(bound, QAST.Const), looplo)):
            raise NotImplementedError("Can't specialize for nonconst bounds")
        ell = np.array([loop.hi.val - loop.lo.val for loop in bounds])
        phis = [[varidx[var] for var in access.support] for access in accesses]

        if(verbose):
            print("ell is: ", ell, " and phis are: ", phis)

        #FIXME deal with cases where you have scalar reads, or slice reads
        # e.g. A[0,i] later. right now it'll crash this.

        #demo_ell = np.array([500, 1500, 10])
        #demo_phis = [[0, 1],  # indexing into C[i,j]
        #            [0, 2],  # indexing into A[i,k]
        #            [2, 1]]  # indexing into B[k,j]
        #demo_M = 1024

        # construct and solve the model
        demo_prob = make_model(ell, phis, memsize)
        demo_prob.solve(verbose=verbose, gp=True)

        # recover the optimal solution
        opt_b = demo_prob.var_dict['b'].value.tolist()
        def round_approx(var, thresh=0.98):
            if var % 1 >= thresh:
                return round(var)
            else:
                return int(var)
        round_b = [round_approx(i) for i in opt_b]
        output_tile = dict([(idxvar[i], round_b[i]) for i in range(len(round_b))])

        return cls(bounds, output_tile)