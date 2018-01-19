from shutil import make_archive, copytree, rmtree
import json
import decimal
import datetime

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

    # write environment data to json file
    env = model.environment
    with open(packaging_path_tmp + '/environment.json', 'w') as outfile:
        json.dump(env.as_dict(), outfile, default=alchemyencoder)

    # write feature set data to json file
    feature_set = model.feature_set
    with open(packaging_path_tmp + '/feature_set.json', 'w') as outfile:
        json.dump(feature_set.as_dict(), outfile, default=alchemyencoder)

    # write single feature data from feature set to json file
    with open(packaging_path_tmp + '/features.json', 'a') as outfile:
            outfile.write('[')
    features = feature_set.features
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
