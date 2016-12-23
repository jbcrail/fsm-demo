registry = {}

def register(cls):
    registry[cls.__clsid__] = cls
    return cls
