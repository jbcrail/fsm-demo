from enum import IntEnum


class UniqueIntEnum(IntEnum):
    """Enum where members are unique and also must be integers"""

    def __init__(self, *args):
        cls = self.__class__
        if any(self.value == e.value for e in cls):
            a = self.name
            e = cls(self.value).name
            raise ValueError("aliases not allowed in %r: %r --> %r" % (cls, a, e))

    @classmethod
    def choices(cls):
        """
        Return a list of tuples representing enumerated choices.
        """
        return [(e.name, e.value) for e in list(cls)]

    @classmethod
    def values(cls):
        """
        Return a list representing all enumerated values.

        This is useful for assigning to a FSM's available states.
        """
        return [e.value for e in list(cls)]
