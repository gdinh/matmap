# MoST_base.py
# Base classes for MoST

import json

class MoSTSchedule:

    # This constructor SHOULD NOT actually implement the schedule
    # For instance, for an autotiler, the constructor should just create 
    # Actually deciding the tile should be the job of a function in /schedules
    # that generates an object of this class (or its subclass).
    def __init__(self):
        pass

    # Apply the transformation to the inputted object.
    # fn's type depends on the backend (e.g. a SysTL function)
    def apply(self, fn, backend="systl"):
        raise NotImplementedError

    # The following (de)serialization will work for any schedule object that
    # only uses basic python data types for members (which is probably most of them)
    # It may be overriden if wished.
    def serialize(self):
        return json.dumps(vars(self))

    @classmethod
    def deserialize(cls, dump):
        rv = cls();
        rv.__dict__ = json.loads(dump)
        return rv

    # Spits out SysTL code that does the same thing as apply()
    # May or may not be a good idea, depending on how important
    # you think the ability to punch through the black box is.
    # Implementing this is optional. Nothing should depend on it.
    # Use serialize() and deserialize() instead
    # Strictly a convenience function to be run by end users.
    def generateBackendCode(self, fn, backend="systl"):
        raise NotImplementedError
        
# object representing multiple transfoms in sequence to represent function composition
class CompoundSchedule(MoSTSchedule):

    def __init__(self, schedule_list, flattenWhenComposed=True):
        for sched in schedule_list:
            assert isinstance(sched, MoSTSchedule), "Non-MoSTSchedule argument passed into CompoundSchedule"

        self.subschedules = schedule_list
        # typically true, so we don't have ridiculous nesting
        # some schedules may want to preserve structure (e.g. subclasses that keep extra metadata)
        self.flattenWhenComposed = flattenWhenComposed
        for subsched in self.subschedules:
            if isinstance(subsched, CompoundSchedule) and subsched.flattenWhenComposed:
                #replace with flattened instance

    def apply(self, fn, backend="systl"):
        transformed = fn
        for subsched in self.schedule_list:
            transformed = subsched.apply(transformed)
        return transformed

    #FIXME do generic (de)serialize  methods work here????


# This object JUST contains a snippet of SysTL code.
# Shouldn't need to be used outside of testing and the like.
# If you actually do need to use it for some reason please let me know, 
# so I can give you something that doesn't need this hack.

class SysTLCodeSchedule(MoSTSchedule):
    def __init__(self, code):
        self.code-snippet = ()