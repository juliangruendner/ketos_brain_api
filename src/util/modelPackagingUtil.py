from shutil import make_archive, copytree, rmtree, unpack_archive
import json
import decimal
import datetime
from util import environmentUtil, mlModelUtil
import uuid
import os
from rdb.models.image import Image
from flask_restful import abort


PACKAGING_PATH_PREFIX = '/ketos/environments_data/packaging/'


def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


def get_packaging_path(model):
    return PACKAGING_PATH_PREFIX + model.environment.container_name


def package_model(model):
    # build relevant paths
    packaging_path = get_packaging_path(model)
    packaging_path_tmp = packaging_path + '/' + model.ml_model_name
    root_dir = '/ketos/environments_data/' + model.environment.container_name + '/' + model.ml_model_name

    # temporarily copy model data to packaging path
    copytree(root_dir, packaging_path_tmp)

    # write model data to json file
    with open(packaging_path_tmp + '/model.json', 'w') as outfile:
        json.dump(model.as_dict(), outfile, default=alchemyencoder)

    # write image data to json file
    image = model.environment.base_image
    with open(packaging_path_tmp + '/image.json', 'w') as outfile:
        json.dump(image.as_dict(), outfile, default=alchemyencoder)

    # write environment data to json file
    env = model.environment
    with open(packaging_path_tmp + '/environment.json', 'w') as outfile:
        json.dump(env.as_dict(), outfile, default=alchemyencoder)

    # write feature set data to json file
    feature_set = model.feature_set
    if feature_set:
        with open(packaging_path_tmp + '/feature_set.json', 'w') as outfile:
            json.dump(feature_set.as_dict(), outfile, default=alchemyencoder)

    # write single feature data from feature set to json file
        with open(packaging_path_tmp + '/features.json', 'a') as outfile:
            outfile.write('[')
        features = feature_set.features
        if features:
            count = 0
            for f in features:
                with open(packaging_path_tmp + '/features.json', 'a') as outfile:
                    json.dump(f.as_dict(), outfile, default=alchemyencoder)
                    count = count + 1
                    if count != len(features):
                        outfile.write(',')
        with open(packaging_path_tmp + '/features.json', 'a') as outfile:
            outfile.write(']')

    # zip data to archive
    archive_name = packaging_path + '/' + model.ml_model_name
    make_archive(archive_name, 'zip', packaging_path_tmp)

    # remove temporary data
    rmtree(packaging_path_tmp)


def abort_if_image_doesnt_exist(self, image_name):
    abort(404, message="image {} doesn't exist".format(image_name))


def load_model(file, abort=True):
    tmp_uuid = str(uuid.uuid4().hex)
    tmp_path = '/tmp/' + tmp_uuid

    os.makedirs(tmp_path, mode=0o777)

    file.save(tmp_path + '/' + file.filename)
    unpack_archive(tmp_path + '/' + file.filename, tmp_path, 'zip')

    create_image = None
    with open(tmp_path + '/image.json', 'r') as infile:
        i = json.load(infile)
        create_image = Image.query.filter_by(name=i['name']).first()
        if abort and not create_image:
            abort_if_image_doesnt_exist(i['name'])

    with open(tmp_path + '/environment.json', 'r') as infile:
        e = json.load(infile)
        env_created = environmentUtil.create_environment(name=e['name'], desc=e['description'], image_id=create_image.id)
    
    with open(tmp_path + '/model.json', 'r') as infile:
        m = json.load(infile)
        mlModelUtil.create_ml_model(name=m['name'], desc=m['description'], env_id=env_created.id, feature_set_id=None)

    rmtree(tmp_path)
