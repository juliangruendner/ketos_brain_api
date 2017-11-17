from rdb.rdb import db


class UserEnvironmentAccess(db.Model):
    __tablename__ = 'user_environment_access'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref("user_link"))
    environment = db.relationship('Environment', backref=db.backref("environment_link"))
