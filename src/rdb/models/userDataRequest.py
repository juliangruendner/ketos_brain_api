from rdb.rdb import db


class UserDataRequest(db.Model):
    __tablename__ = 'user_data_request'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    datarequest_id = db.Column(db.Integer, db.ForeignKey('data_request.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref("user_data_request_link"))
    data_request = db.relationship('DataRequest', backref=db.backref("user_data_request_link"))