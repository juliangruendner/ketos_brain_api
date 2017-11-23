from rdb.rdb import db


class UserGroupAssignment(db.Model):
    __tablename__ = 'user_group_assignment'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref("user_group_link"))
    group = db.relationship('UserGroup', backref=db.backref("group_user_link"))
