from rdb.rdb import db, LowerCaseText
import datetime
from flask_restful import abort
from flask import g


class Image(db.Model):
    """Image class"""

    __tablename__ = "image"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(LowerCaseText, unique=True, nullable=False)
    title = db.Column(db.Text)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    environments_based_on_this = db.relationship('Environment', lazy=True, backref='base_image')
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)

    def __init__(self):
        super(Image, self).__init__()

    def __repr__(self):
        """Display when printing a image object"""

        return "<ID: {}, description: {}>".format(self.id, self.desription)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def abort_if_image_doesnt_exist(self, image_id):
    abort(404, message="image {} doesn't exist".format(image_id))


def get(image_id, raise_abort=True):
    i = Image.query.get(image_id)

    if raise_abort and not i:
        abort_if_image_doesnt_exist(image_id)

    return i


def get_by_name(image_name, raise_abort=True):
    image = Image.query.filter_by(name=image_name).first()

    if raise_abort and not image:
        abort_if_image_doesnt_exist(image_name)

    return image


def get_all():
    return Image.query.all()


def create(name, desc, title, creator_id=None):
    i = Image()
    i.name = name
    i.description = desc
    i.title = title
    if not creator_id:
        i.creator_id = g.user.id
    else:
        i.creator_id = creator_id

    db.session.add(i)
    db.session.commit()

    return i
