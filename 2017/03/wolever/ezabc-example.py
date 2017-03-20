import ezabc
from autorepr import autorepr

class User(object):
    def __init__(self, id, first_name, last_name):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

    __repr__ = autorepr(["id", "first_name", "last_name"])


class UserServiceBase(object):
    __metaclass__ = ezabc.ABCMeta

    def get_user_by_id(self, user_id):
        raise NotImplementedError()

    def get_user_full_name(self, user_id):
        user = self.get_user_by_id(user_id)
        return "%s %s" %(user.first_name, user.last_name)


class DatabaseUserService(UserServiceBase):
    def get_user_by_id(self, user_id):
        return User(123, "Jane", "Wong")


service = DatabaseUserService()
print "User:", service.get_user_by_id(123)
