import pkgutil

prefix = __name__ + '.'
__path__ = pkgutil.extend_path(__path__, __name__)
for _, modname, _ in pkgutil.walk_packages(path=__path__, prefix=prefix):
    __import__(modname)
