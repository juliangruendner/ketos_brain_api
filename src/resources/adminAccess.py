from flask import g
from flask_restful import abort
import functools


class AdminAccess(object):
    def __init__(self):
        return

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            if not is_admin_user():
                abort(403, message="only admin user may use this function")
            return fn(*args, **kwargs)
        return decorated


def is_admin_user():
    if not g.user.username == "admin":
        return False

    return True
