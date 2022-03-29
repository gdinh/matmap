from __future__ import annotations
import sys
from exo import proc, Procedure, DRAM, config, instr, QAST
from collections import namedtuple
from itertools import chain

ForLoop = namedtuple("ForLoop", ["name", "lo", "hi"])
DataAccess = namedtuple("DataAccess", ["name", "idx", "type"])
ProjectiveDataAccess = namedtuple("ProjectiveDataAccess", ["name", "support"])

# nest: the loop nest to point to
# order: which occurrence? 0 for first, 1 for 2nd, etc.
def readLoopNest(nest, order=0):
  assert type(order) is int, "Wrong type in order arg of getLoopVarsAndBounds"
  loops = nest.get_ast("for _ in _: _ #" + str(order))
  assert type(loops) is list and len(loops) >= 1
  assert isinstance(loops[0], QAST.For)

  body = None

  def recurse_loops(loops):
    if len(loops) < 1:
      return []
    stmt = loops[0]
    assert isinstance(stmt, QAST.Stmt)
    if isinstance(stmt, QAST.For):
      return [ForLoop(stmt.name, stmt.lo, stmt.hi)] + recurse_loops(stmt.body)
    else:
      nonlocal body
      body = loops
      return []

  return recurse_loops(loops), body

def getNestBounds(nest, order=0):
  return readLoopNest(nest, order)[0]

def getNestVars(nest, order=0):
  return [i.name for i in getNestBounds(nest, order)]

# NB: right now, we don't support nonuniform accesses
# for instance, A[B[i]] is not supported
# in that case the current behavior is to return a DataAccess
# with idx = B[i] but NOT to record B[i] as an eccess
def getDataAccesses(nest, order=0):
  body = readLoopNest(nest, order)[1]
  if len(body) < 1:
    return []
  
  def recurse_accesses(stmt):
    if isinstance(stmt, list):
      return list(chain.from_iterable(map(recurse_accesses, stmt)))
    else:
      assert isinstance(stmt, QAST.Stmt) or isinstance(stmt, QAST.Expr)

    if isinstance(stmt, QAST.Assign):
      return [DataAccess(stmt.name, stmt.idx, stmt.lhs_type)] + recurse_accesses(stmt.rhs)
    elif isinstance(stmt, QAST.Reduce):
      return [DataAccess(stmt.name, stmt.idx, stmt.lhs_type)] + recurse_accesses(stmt.rhs)
    elif isinstance(stmt, QAST.Read):
      return [DataAccess(stmt.name, stmt.idx, stmt.type)]
    elif isinstance(stmt, QAST.BinOp):
      return recurse_accesses(stmt.lhs) + recurse_accesses(stmt.rhs)
    elif isinstance(stmt, QAST.Const):
      return []
    else:
      raise NotImplementedError("can't handle QAST type", str(type(stmt)))

  accesses = recurse_accesses(body)
  
  # checks for pointer-chasing
  # probably not necessary, because you'll end up with f32 vs int type errors
  # if you try to do it right now, but for future-proofing
  for access in accesses:
    sub_accesses = recurse_accesses(access.idx)
    if any(map(lambda sa: sa.idx != [], sub_accesses)):
      raise NotImplementedError("pointer-chasing not supported")

  return accesses

def getProjectiveDataAccesses(nest, order=0):
  accesses = getDataAccesses(nest, order)
  loop_vars = list(map(lambda l: l.name, getNestBounds(nest, order)))
  projections = []

  # make sure that indices are projections
  for array_access in accesses:
    proj = []
    #indices is a list of QAST exprs, one for each component
    #if we're reading a scalar in DRAM, then idx is []
    indices = array_access.idx
    for index in indices:
      if isinstance(index, QAST.Read):
        assert index.idx == [], "pointer chasing found"
        assert index.name in loop_vars, "index that is not loop index found, non-projective"
        proj += [index.name]
      elif isinstance(index, QAST.Const):
        proj += [index.val]
      else:
        assert False, "Data access isn't projective!"
    projections += [ProjectiveDataAccess(array_access.name, proj)]
  return projections

def getFixedLoopBounds(nest, order=0):
  loops = getNestBounds(nest, order)
  for loop in loops:
    assert isinstance(loop.lo, QAST.Const)
    assert isinstance(loop.hi, QAST.Const)
  return list(map(lambda loop: ForLoop(loop.name, loop.lo.val, loop.hi.val), loops))

#debug helpers - delete after done

def __debug_new_sgemm():
  @proc
  def sgemm_full(
      N: size,
      M: size,
      K: size,
      C: f32[N, M] @ DRAM,
      A: f32[N, K] @ DRAM,
      B: f32[K, M] @ DRAM,
      #D: f32[N, M] @ DRAM,
      #E: f32 @ DRAM

  ):
      for i in par(0, N):
          for j in par(0, M):
              for k in par(0, K):
                  #D[i,j] = A[0,0] + E
                  C[i, j] += A[i, k] * B[k, j]
  return sgemm_full