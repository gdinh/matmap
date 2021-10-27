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
    def __init__(self, loop_bounds, tile_bounds):
        self.loop_bounds = loop_bounds
        self.tile_bounds = tile_bounds

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
        return fn

