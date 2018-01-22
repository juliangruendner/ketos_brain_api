from flask import g
from rdb.rdb import db
from rdb.models.featureSet import FeatureSet


def create_feature_set(name, desc):
    fs = FeatureSet()
    fs.name = name
    fs.description = desc
    fs.creator_id = g.user.id

    db.session.add(fs)
    db.session.commit()
    return fs
