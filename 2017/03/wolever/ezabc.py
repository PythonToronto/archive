import inspect

class ABCMeta(type):
    """ A very simple abstract base class implementation which verifies,
        at compile time, that subclasses implement all required abstract
        methods.

        Methods are considered abstract if their implementation contains the
        string ``raise NotImplementedError``.

        For example::

            class BaseClass(object):
                __metaclass__ = ABCMeta

                def concrete_method(self):
                    return 42

                def abstract_method(self):
                    raise NotImplementedError()

            class ConcreteClass(BaseClass):
                # No error will be raised because ``ConcreteClass`` implements
                # ``abstract_method``.
                def abstract_method(self):
                    return 16

            class InvalidConcreteClass(BaseClass):
                # An error will be raised because ``InvalidConcreteClass``
                # doesn't implement ``abstract_method``.
                pass

            class Mixin(object):
                def abstract_method(self):
                    return 7

            class ValidCocreteClassWithMixin(Mixin, BaseClass):
                # No error will be raised because ``Mixin`` implements
                # ``abstract_method``.
                pass

        """

    def __new__(meta, name, bases, namespace):
        cls = super(ABCMeta, meta).__new__(meta, name, bases, namespace)
        missing_methods = cls_get_missing_abstract_methods(cls)
        if missing_methods:
            raise TypeError(
                "%s(%s) does not implement expected abstract methods: %s" %(
                    cls.__name__,
                    ", ".join(c.__name__ for c in bases),
                    ", ".join(missing_methods),
                ),
            )
        return cls


def is_abstract_method(val):
    try:
        source = inspect.getsource(val)
    except IOError:
        return False
    return "raise NotImplementedError" in source

def cls_get_missing_abstract_methods(cls):
    implemented_methods = set()
    missing_abstract_methods = {}
    for c in cls.__mro__:
        for name, val in c.__dict__.items():
            if not inspect.isfunction(val):
                continue
            if c != cls and is_abstract_method(val):
                if name not in implemented_methods:
                    missing_abstract_methods[name] = c.__name__
                continue
            implemented_methods.add(name)

    return [
        "%s.%s" %(cls_name, name)
        for (name, cls_name)
        in missing_abstract_methods.items()
    ]
