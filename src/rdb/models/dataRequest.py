from rdb.rdb import db
import datetime
from flask import g
from flask_restful import abort
import rdb.models.user as User


class DataRequest(db.Model):
    """Data Request Class"""

    __tablename__ = "data_request"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text)
    request_id = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('User', lazy='subquery', secondary='user_data_request')

    def __init__(self):
        super(DataRequest, self).__init__()

    def __repr__(self):
        """Display when printing a Request object"""

        return "<ID: {}, request id: {}, creator id: {}, users: {}>".format(self.id, self.request_id, self.creator_id, self.users)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def create(request_id, creator_id=None):

    dr = DataRequest()
    dr.request_id = request_id

    if not creator_id:
        dr.creator_id = g.user.id
    else:
        dr.creator_id = creator_id

    db.session.add(dr)
    db.session.commit()
    return dr


def get(data_request_id, raise_abort=True):

    dr = DataRequest.query.get(data_request_id)

    if raise_abort and not dr:
        abort_if_data_request_doesnt_exist(data_request_id)

    return dr


def abort_if_data_request_doesnt_exist(data_request_id):
    abort(404, message="data request {} doesn't exist".format(data_request_id))


def get_all():
    return DataRequest.query.all()


def get_all_for_user(user_id):
    return db.session.query(DataRequest.request_id).filter(DataRequest.users.any(id=user_id)).all()

def get_by_request_id(request_id):
    return DataRequest.query.filter_by(request_id=request_id).first()


def update(data_request_id, creator_id=None, raise_abort=True):
    dr = get(data_request_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(dr.creator_id)

    if creator_id:
        dr.creator_id = creator_id

    db.session.commit()
    return dr, 200

def add_users(data_request_id, user_ids, raise_abort=True):
    dr = get_by_request_id(data_request_id)
    for id in user_ids:
        u = User.get(id, raise_abort=raise_abort)
        if u not in dr.users:
            dr.users.append(u)

    db.session.commit()
    return dr


def delete(data_request_id, raise_abort=True):
    dr = get(data_request_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(dr.creator_id)

    db.session.delete(dr)
    db.session.commit()

    return data_request_id
