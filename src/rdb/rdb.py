from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.types as types
import config


db = SQLAlchemy()


class LowerCaseText(types.TypeDecorator):
    '''Converts strings to lower case on the way in.'''

    impl = types.Text

    def process_bind_param(self, value, dialect):
        return value.lower()


def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + config.POSTGRES_USER + ':' + config.POSTGRES_PASSWORD + '@'+ config.POSTGRES_HOST + ':5432/' + config.POSTGRES_DB
    db.app = app
    db.init_app(app)


def create_all():
    """Create all db tables"""

    from rdb.models.user import User
    from rdb.models.environment import Environment
    # from rdb.models.userEnvironmentAccess import UserEnvironmentAccess
    from rdb.models.image import Image
    from rdb.models.mlModel import MLModel
    from rdb.models.feature import Feature
    from rdb.models.featureSet import FeatureSet
    from rdb.models.featureFeatureSet import FeatureFeatureSet
    from rdb.models.predictionOutcome import PredictionOutcome
    from rdb.models.dataRequest import DataRequest
    from rdb.models.userDataRequest import UserDataRequest

    db.create_all()
    db.session.commit()


def create_admin_user():
    """create admin user while startup"""

    import rdb.models.user as User

    u = User.get_by_username('admin', raise_abort=False)

    if not u:
        u = User.create(username=config.ML_SERVICE_ADMIN_USERNAME, email=config.ML_SERVICE_ADMIN_EMAIL, password=config.ML_SERVICE_ADMIN_PASSWORD)


def create_default_images():
    import rdb.models.image as Image
    import rdb.models.user as User

    i = Image.get_by_name(image_name="ketos_env_r")
    if not i:
        i = Image.create(name="ketos_env_r", desc="Basic R datascience image", title="R image", creator_id=User.get_by_username("admin", raise_abort=False).id)

    j = Image.get_by_name(image_name="ketos_env_ds")
    if not j:
        j = Image.create(name="ketos_env_ds", desc="DataSHIELD image", title="DataSHIELD image", creator_id=User.get_by_username("admin", raise_abort=False).id)

def create_default_features():
    """create default feastures while startup"""

    import rdb.models.featureSet as FeatureSet
    import rdb.models.feature as Feature
    import rdb.models.user as User

    fs = FeatureSet.get_all()
    creator_id = User.get_by_username("admin", raise_abort=False).id

    if not fs or len(fs) == 0:
        fs = FeatureSet.create(name='getting_started', desc='getting started example', creator_id=creator_id)

        feature_names = ['rateOfGrowth', 'bodyWeight', 'bodyHeight', 'bodySize', 'bodyComposition']
        feature_code_values = ['800000009', '800000001', '800000002', '800000003', '800000004']

        for index in range(0, len(feature_names)):
            f = Feature.create(resource='Observation', parameter_name='code', value=feature_code_values[index], name=feature_names[index], desc='test description', creator_id=creator_id)
            fs.features.append(f)
            db.session.commit()
