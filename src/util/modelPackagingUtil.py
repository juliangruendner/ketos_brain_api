from shutil import make_archive, copytree, rmtree, unpack_archive, move
import json
import decimal
import datetime
import uuid
import os
import rdb.models.image as Image
import rdb.models.mlModel as MLModel
import rdb.models.feature as Feature
import rdb.models.featureSet as FeatureSet
import rdb.models.environment as Environment
from rdb.rdb import db


PACKAGING_PATH_PREFIX = '/ketos/environments_data/packaging/'
METADATA_DIR = '/ketos_metadata'


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
    metadata_path = packaging_path_tmp + METADATA_DIR
    root_dir = model.environment.get_data_directory() + '/' + model.ml_model_name

    # initial cleanup
    if os.path.isdir(packaging_path_tmp):
        rmtree(packaging_path_tmp)

    # temporarily copy model data to packaging path
    copytree(root_dir, packaging_path_tmp)

    # create directory for metadata
    os.makedirs(metadata_path, mode=0o777)

    # write model data to json file
    with open(metadata_path + '/model.json', 'w') as outfile:
        json.dump(model.as_dict(), outfile, default=alchemyencoder)

    # write image data to json file
    image = model.environment.base_image
    with open(metadata_path + '/image.json', 'w') as outfile:
        json.dump(image.as_dict(), outfile, default=alchemyencoder)

    # write environment data to json file
    env = model.environment
    with open(metadata_path + '/environment.json', 'w') as outfile:
        json.dump(env.as_dict(), outfile, default=alchemyencoder)

    # write feature set data to json file
    feature_set = model.feature_set
    if feature_set:
        with open(metadata_path + '/feature_set.json', 'w') as outfile:
            json.dump(feature_set.as_dict(), outfile, default=alchemyencoder)

    # write single feature data from feature set to json file
        with open(metadata_path + '/features.json', 'a') as outfile:
            outfile.write('[')
        features = feature_set.features
        if features:
            count = 0
            for f in features:
                with open(metadata_path + '/features.json', 'a') as outfile:
                    json.dump(f.as_dict(), outfile, default=alchemyencoder)
                    count = count + 1
                    if count != len(features):
                        outfile.write(',')
        with open(metadata_path + '/features.json', 'a') as outfile:
            outfile.write(']')

    # zip data to archive
    archive_path = packaging_path + '/' + model.ml_model_name
    if os.path.exists(archive_path + '.zip'):
        os.remove(archive_path + '.zip')
    make_archive(archive_path, 'zip', packaging_path_tmp)

    # remove temporary data
    rmtree(packaging_path_tmp)


def load_model(file, raise_abort=True):
    # generate temporary path to save file to
    tmp_uuid = str(uuid.uuid4().hex)
    tmp_path = '/tmp/' + tmp_uuid

    # create temporary directory
    os.makedirs(tmp_path, mode=0o777)

    # save zip-file to temporary directory and unzip it
    file.save(tmp_path + '/' + file.filename)
    unpack_archive(tmp_path + '/' + file.filename, tmp_path, 'zip')
    os.remove(tmp_path + '/' + file.filename)

    # first of all: get the image of the environment to create
    create_image = None
    with open(tmp_path + METADATA_DIR + '/image.json', 'r') as infile:
        i = json.load(infile)
        create_image = Image.get_by_name(image_name=i['name'])

    # create and start the new environment
    env_created = None
    with open(tmp_path + METADATA_DIR + '/environment.json', 'r') as infile:
        e = json.load(infile)
        env_created = Environment.create(name=e['name'], desc=e['description'], image_id=create_image.id)

    # create the model which is to be loaded
    model_created = None
    with open(tmp_path + METADATA_DIR + '/model.json', 'r') as infile:
        m = json.load(infile)
        model_created = MLModel.create(name=m['name'], desc=m['description'], env_id=env_created.id, create_example_model=False, feature_set_id=None)

    if os.path.isfile(tmp_path + METADATA_DIR + '/features.json') and os.path.isfile(tmp_path + METADATA_DIR + '/feature_set.json'):
        # create the features
        features_created = list()
        with open(tmp_path + METADATA_DIR + '/features.json', 'r') as infile:
            fs = json.load(infile)
            for f in fs:
                feature = Feature.get_by_res_par_val(resource=f['resource'], parameter_name=f['parameter_name'], value=f['value'])
                if not feature:
                    feature = Feature.create(resource=f['resource'], parameter_name=f['parameter_name'], value=f['value'], name=f['name'], desc=f['description'])
                features_created.append(feature)

        # create the feature set with the features and model assigned
        with open(tmp_path + METADATA_DIR + '/feature_set.json', 'r') as infile:
            fs = json.load(infile)
            feature_set_created = FeatureSet.create(name=fs['name'], desc=fs['description'])
            feature_set_created.features = features_created
            feature_set_created.ml_models.append(model_created)
            db.session.commit()

    # remove temporarily created directory and files
    rmtree(env_created.get_data_directory() + '/' + model_created.ml_model_name)
    os.makedirs(env_created.get_data_directory() + '/' + model_created.ml_model_name, mode=0o777)
    for filename in os.listdir(tmp_path):
        move(tmp_path + '/' + filename, env_created.get_data_directory() + '/' + model_created.ml_model_name)
    rmtree(env_created.get_data_directory() + '/' + model_created.ml_model_name + METADATA_DIR)
