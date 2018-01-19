from flask import g
from flask_restful import abort
from rdb.rdb import db
from rdb.models.environment import Environment
from rdb.models.mlModel import MLModel
import requests
from rdb.models.featureSet import FeatureSet


def abort_if_environment_doesnt_exist(env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))


def get_feature_set(feature_set_id):
    fs = FeatureSet.query.get(feature_set_id)

    if not fs:
        abort_if_feature_set_doesnt_exist(feature_set_id)

    return fs


def abort_if_feature_set_doesnt_exist(feature_set_id):
    abort(404, message="feature set {} doesn't exist".format(feature_set_id))


def create_ml_model(name, desc, env_id, feature_set_id, abort=True):
    e = Environment.query.get(env_id)

    if abort and not e:
        abort_if_environment_doesnt_exist(env_id)

    m = MLModel()
    m.environment_id = e.id
    m.name = name
    m.description = desc
    m.creator_id = g.user.id

    resp = requests.post('http://' + e.container_name + ':5000/models').json()
    m.ml_model_name = str(resp['modelName'])

    if feature_set_id:
        fs = get_feature_set(feature_set_id)
        m.feature_set_id = fs.id

    db.session.add(m)
    db.session.commit()
    
    return m
