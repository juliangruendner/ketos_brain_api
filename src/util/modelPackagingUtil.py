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

    # create metadata json file
    with open(metadata_path + '/metadata.json', 'w') as metadata:
        metadata.write('[')

        # write image data to json file
        image = model.environment.base_image
        json.dump(image.as_dict(), metadata, default=alchemyencoder)
        metadata.write(',')

        # write environment data to json file
        env = model.environment
        json.dump(env.as_dict(), metadata, default=alchemyencoder)
        metadata.write(',')

        # write model data to json file
        json.dump(model.as_dict(), metadata, default=alchemyencoder)

        # write feature set data to json file
        feature_set = model.feature_set
        if feature_set:
            metadata.write(',')

            # write single feature data from feature set to json file
            metadata.write('[')
            features = feature_set.features
            if features:
                count = 0
                for f in features:
                    json.dump(f.as_dict(), metadata, default=alchemyencoder)
                    count = count + 1
                    if count != len(features):
                        metadata.write(',')
            metadata.write(']')

            metadata.write(',')
            json.dump(feature_set.as_dict(), metadata, default=alchemyencoder)

        metadata.write(']')

    # zip data to archive
    archive_path = packaging_path + '/' + model.ml_model_name
    if os.path.exists(archive_path + '.zip'):
        os.remove(archive_path + '.zip')
    make_archive(archive_path, 'zip', packaging_path_tmp)

    # remove temporary data
    rmtree(packaging_path_tmp)


def load_model(file, environment_id=None, feature_set_id=None, raise_abort=True):
    # generate temporary path to save file to
    tmp_uuid = str(uuid.uuid4().hex)
    tmp_path = '/tmp/' + tmp_uuid

    # create temporary directory
    os.makedirs(tmp_path, mode=0o777)

    # save zip-file to temporary directory and unzip it
    file.save(tmp_path + '/' + file.filename)
    unpack_archive(tmp_path + '/' + file.filename, tmp_path, 'zip')
    os.remove(tmp_path + '/' + file.filename)

    # load metadata
    metadata = None
    with open(tmp_path + METADATA_DIR + '/metadata.json', 'r') as infile:
        metadata = json.load(infile)

    # first of all: get the image of the environment to create
    i = metadata[0]
    create_image = Image.get_by_name(image_name=i['name'])

    # create and start the new environment
    env_created = None
    e = metadata[1]
    if not environment_id or environment_id <= 0:
        env_created = Environment.create(name=e['name'], desc=e['description'], image_id=create_image.id)
    else:
        env_created = Environment.get(environment_id, raise_abort=raise_abort)

    # create the model which is to be loaded
    m = metadata[2]
    model_created = MLModel.create(name=m['name'], desc=m['description'], env_id=env_created.id, create_example_model=False, feature_set_id=None)

    if len(metadata) > 3:
        # create the features
        features_created = list()
        features = metadata[3]
        for f in features:
            # do not create duplicate features
            feature = Feature.get_by_res_par_val(resource=f['resource'], parameter_name=f['parameter_name'], value=f['value'])
            if not feature:
                feature = Feature.create(resource=f['resource'], parameter_name=f['parameter_name'], value=f['value'], name=f['name'], desc=f['description'])
            features_created.append(feature)

        # create the feature set with the features and model assigned
        feature_set_created = None
        fs = metadata[4]

        if not feature_set_id or feature_set_id <= 0:
            feature_set_created = FeatureSet.create(name=fs['name'], desc=fs['description'])
        else:
            feature_set_created = FeatureSet.get(feature_set_id, raise_abort=raise_abort)

        feature_set_created.features = features_created
        feature_set_created.ml_models.append(model_created)
        db.session.commit()

    # remove temporarily created directory and files
    rmtree(env_created.get_data_directory() + '/' + model_created.ml_model_name)
    os.makedirs(env_created.get_data_directory() + '/' + model_created.ml_model_name, mode=0o777)
    for filename in os.listdir(tmp_path):
        move(tmp_path + '/' + filename, env_created.get_data_directory() + '/' + model_created.ml_model_name)
    rmtree(env_created.get_data_directory() + '/' + model_created.ml_model_name + METADATA_DIR)
