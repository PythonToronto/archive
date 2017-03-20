class User(object):
    max_name_length = 128

    def get_name(self):
        return self.name


User = type("User", (object, ), {
    "max_name_length": 128,
    "get_name": lambda self: self.name,
})


class MyFirstMeta(type):
    def __new__(meta, name, bases, attrs):
        print "Creating new class %r with:" %(name, )
        print "  Bases: %r" %(bases, )
        print "  Attrs:"
        print "\n".join("%18s: %r" %x for x in attrs.items())
        return super(MyFirstMeta, meta).__new__(meta, name, bases, attrs)

print "BEFORE CLASS DEFINITION\n\n"

class UserWithMyMeta(object):
    __metaclass__ = MyFirstMeta

    max_name_length = 128

    def get_name(self):
        return self.name


print "\n\nAFTER CLASS DEFINITION\n\n"

print "type(User):          ", type(User)
print "type(UserWithMyMeta):", type(UserWithMyMeta)
