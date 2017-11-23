from flask import g
from flask_restful import abort
import functools


class AuthorizedGroups(object):
    def __init__(self, *args):
        self.args = args

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            authorized = False

            for gr in g.user.assigned_groups:
                if gr.name in str(self.args):
                    authorized = True
                    break

            if not authorized:
                abort(403, message="Not assigned to one of the authorized groups")
            return fn(*args, **kwargs)
        return decorated
