import json
import logging
import logging.config
logging.config.dictConfig(json.load(open("logging_config.json", "r")))

from flask import Flask
from flask_restful_swagger_2 import Api
from resources.userResource import UserListResource, UserResource, UserLoginResource
from resources.imageResource import ImageListResource, ImageResource
from resources.environmentResource import EnvironmentListResource, EnvironmentResource, UserEnvironmentListResource
from resources.featureResource import FeatureListResource, FeatureResource, UserFeatureListResource
from resources.featureSetResource import FeatureSetListResource, FeatureSetResource, UserFeatureSetListResource, FeatureSetFeatureListResource
from resources.mlModelResource import MLModelListResource, MLModelResource, UserMLModelListResource, MLModelPredicitionResource
from resources.mlModelResource import MLModelExportResource, MLModelImportResource, MLModelImportSuitableEnvironmentResource, MLModelImportSuitableFeatureSetResource
from resources.dataResource import DataListResource, DataResource
from resources.resourceConfigResource import ResourceConfigList
from rdb.rdb import connect_to_db, create_all, create_admin_user, create_default_images, create_default_features
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app, add_api_spec_resource=True, api_version='0.0', api_spec_url='/api/swagger')  # Wrap the Api and add /api/swagger endpoint

connect_to_db(app)
create_all()
create_admin_user()
create_default_images()
create_default_features()

CORS(app)

api.add_resource(UserListResource, '/users', endpoint='users')
api.add_resource(UserLoginResource, '/users/login', endpoint='user_login')
api.add_resource(UserResource, '/users/<int:user_id>', endpoint='user')
api.add_resource(UserEnvironmentListResource, '/users/<int:user_id>/environments', endpoint='environments_for_user')
api.add_resource(UserMLModelListResource, '/users/<int:user_id>/models', endpoint='models_for_user')
api.add_resource(UserFeatureListResource, '/users/<int:user_id>/features', endpoint='features_for_user')
api.add_resource(UserFeatureSetListResource, '/users/<int:user_id>/featuresets', endpoint='feature_sets_for_user')
api.add_resource(EnvironmentListResource, '/environments', endpoint='environments')
api.add_resource(EnvironmentResource, '/environments/<int:env_id>', endpoint='environment')
api.add_resource(MLModelListResource, '/models', endpoint='models')
api.add_resource(MLModelResource, '/models/<int:model_id>', endpoint='model')
api.add_resource(MLModelExportResource, '/models/<int:model_id>/export', endpoint='model_export')
api.add_resource(MLModelImportResource, '/models/import', endpoint='model_import')
api.add_resource(MLModelImportSuitableEnvironmentResource, '/models/import/suitable-environments', endpoint='model_import_suitable_environments')
api.add_resource(MLModelImportSuitableFeatureSetResource, '/models/import/suitable-feature-sets', endpoint='model_import_suitable_feature_sets')
api.add_resource(MLModelPredicitionResource, '/models/<int:model_id>/prediction', endpoint='model_prediction')
api.add_resource(ImageListResource, '/images', endpoint='images')
api.add_resource(ImageResource, '/images/<int:image_id>', endpoint='image')
api.add_resource(DataListResource, '/data', endpoint='datalist')
api.add_resource(DataResource, '/data/<datarequest_id>', endpoint='data')
api.add_resource(FeatureListResource, '/features', endpoint='features')
api.add_resource(FeatureResource, '/features/<int:feature_id>', endpoint='feature')
api.add_resource(FeatureSetListResource, '/featuresets', endpoint='feature_sets')
api.add_resource(FeatureSetResource, '/featuresets/<int:feature_set_id>', endpoint='feature_set')
api.add_resource(FeatureSetFeatureListResource, '/featuresets/<int:feature_set_id>/features', endpoint='feature_set_features')
api.add_resource(ResourceConfigList, '/resources_config', endpoint='resources_config')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
