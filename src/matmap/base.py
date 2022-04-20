# base.py
# Base classes for MoST

import json

class Transform:

    # This constructor SHOULD NOT actually implement the schedule
    # For instance, for an autotiler, the constructor should just create 
    # Actually deciding the tile should be the job of a function in /schedules
    # that generates an object of this class (or its subclass).
    def __init__(self):
        pass

    # Apply the transformation to the inputted object.
    # fn's type depends on the backend (e.g. an exo function)
    def apply(self, fn, backend="exo"):
        raise NotImplementedError

    # The following (de)serialization will work for any schedule object that
    # only uses basic python data types for members (which is probably most of them)
    # It may be overriden if wished.
    # TODO: probably a bit hacky with some non-obvious pitfalls. suggestions for improvement:
    # https://hynek.me/articles/serialization/
    # https://marshmallow.readthedocs.io/en/stable/
    # https://desert.readthedocs.io/en/stable/
    def serialize(self):
        dump = dict()
        #dump['__class__'] = self.__class__
        #dump['__module__'] = self.__module__
        for field in self.fields():
            dump[field] = getattr(self, field)
        return json.dumps(dump)

    #can and should override this for anything with temp vars
    def fields(self):
        return vars(self).keys()

    @classmethod
    def deserialize(cls, dump):
        """
        var_dict = json.loads(dump)

        sched_type_str = var_dict['_schedule_type']
        #just some basic validation here, so you can't blow up your system with bad input
        valid_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'
        for char in sched_type_str:
            assert char in valid_chars, "deserialize: invalid character in _schedule_type of input JSON"
        
        fields = eval(sched_type + '()')
        rv.__dict__ = var_dict
        """
        rv = cls()
        fieldVals = json.loads(dump)
        for fieldName in fieldVals:
            setattr(rv, fieldName, fieldVals[fieldName])
        return rv

    # Spits out exo code that does the same thing as apply()
    # May or may not be a good idea, depending on how important
    # you think the ability to punch through the black box is.
    # Implementing this is optional. Nothing should depend on it.
    # Use serialize() and deserialize() instead
    # Strictly a convenience function to be run by end users.
    def generateBackendCode(self, fn, backend="exo"):
        raise NotImplementedError

# object representing multiple transfoms in sequence to represent function composition
class CompoundTransform(Transform):

    def __init__(self, schedule_list, flattenWhenComposed=True):
        self.subschedules = []
        # typically true, so we don't have ridiculous nesting
        # some schedules may want to preserve structure (e.g. subclasses that keep extra metadata)
        self.flattenWhenComposed = flattenWhenComposed
        for subsched in schedule_list:
            assert isinstance(subsched, Transform), "Non-MoSTSchedule argument passed into CompoundSchedule"
            if isinstance(subsched, CompoundTransform) and subsched.flattenWhenComposed:
                self.subschedules.extend(subsched.subschedules)
            else:
                self.subschedules.append(subsched)

    def apply(self, fn, backend="exo"):
        transformed = fn
        for subsched in self.subschedules:
            transformed = subsched.apply(transformed)
        return transformed

    # TODO: figure out how to deal with nested input.
    # there are some libraries for this, probably better than this hack
    def serialize(self):
        serialized_subschedules = map(lambda sched: sched.serialize(), self.subschedules)
        return json.dumps(vars(self))


# This object JUST contains a snippet of exo code.
# Shouldn't be used most of the time, but may be useful if you
# need to, say, run a few explicit exo calls within a CompoundSchedule
# Probably dangerous.

class ExoCodeTransform(Transform):
    def __init__(self, code):
        pass