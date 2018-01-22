from flask import g
from rdb.rdb import db
from rdb.models.feature import Feature


def create_feature(resource, parameter_name, value, name, desc):
    f = Feature()
    f.resource = resource
    f.parameter_name = parameter_name
    f.value = value
    f.name = name
    f.description = desc
    f.creator_id = g.user.id

    db.session.add(f)
    db.session.commit()
    return f
