from __future__ import annotations
from cmath import cos
import sys
from exo import proc, Procedure, DRAM, config, instr, QAST
from matmap.base import *
from matmap.qast_utils.loopReader import *
from itertools import dropwhile

class ReorderingTransform(Transform):
    #loop bounds are a ForLoop object
    #tile_bounds is a dict mapping names from the ForLoop to numbers
    def __init__(self, loop_order):
        self.loop_order = loop_order
        
    def apply(self, fn, backend="exo"):
        def get_loop_order(obj):
            loops = readLoopNest(obj)[0]
            loop_list = []
            for loop in loops:
                loop_list.append(loop.name)
            return loop_list
        loop_dict = {}
        to_list = []
        num = 0
        for i in self.loop_order:
            loop_dict[num] = i
            to_list.append(num)
            num += 1
        given_list = []
        new_dict = {value : key for (key, value) in loop_dict.items()}
        for i in get_loop_order(fn):
            given_list.append(new_dict[i])
        
        #sort values and swap elements 
        n = len(given_list)
        for i in range(n):
                for j in range(n - 1):
                    if given_list[j] > given_list[j+1]:
                        fn = fn.reorder(loop_dict[given_list[j]], loop_dict[given_list[j+1]])
                        given_list[j], given_list[j+1] = given_list[j+1], given_list[j]    
        return fn



    
    