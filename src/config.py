import os

POSTGRES_USER = str(os.getenv('POSTGRES_USER', ''))
POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD', ''))
POSTGRES_DB = str(os.getenv('POSTGRES_DB', ''))
POSTGRES_HOST = str(os.getenv('POSTGRES_HOST', ''))

DOCKER_REGISTRY_USERNAME = str(os.getenv('DOCKER_REGISTRY_USERNAME', ''))
DOCKER_REGISTRY_PASSWORD = str(os.getenv('DOCKER_REGISTRY_PASSWORD', ''))
DOCKER_REGISTRY_URL = str(os.getenv('DOCKER_REGISTRY_URL', ''))
DOCKER_REGISTRY_DOMAIN = str(os.getenv('DOCKER_REGISTRY_DOMAIN', ''))

ML_SERVICE_ADMIN_USERNAME = str(os.getenv('ML_SERVICE_ADMIN_USERNAME', ''))
ML_SERVICE_ADMIN_EMAIL = str(os.getenv('ML_SERVICE_ADMIN_EMAIL', ''))
ML_SERVICE_ADMIN_PASSWORD = str(os.getenv('ML_SERVICE_ADMIN_PASSWORD', ''))

PROJECT_NAME = str(os.getenv('PROJECT_NAME', ''))

DATA_PREPROCESSING_HOST = str(os.getenv('DATA_PREPROCESSING_HOST', ''))

HAPIFHIR_URL = str(os.getenv('HAPIFHIR_URL', ''))

ANNOTATION_API_HOST = str(os.getenv('ANNOTATION_API_HOST', ''))

OMOP_ON_FHIR_POSTGRES_USER = str(os.getenv('OMOP_ON_FHIR_POSTGRES_USER', ''))
OMOP_ON_FHIR_POSTGRES_PASSWORD = str(os.getenv('OMOP_ON_FHIR_POSTGRES_PASSWORD', ''))
OMOP_ON_FHIR_POSTGRES_DB = str(os.getenv('OMOP_ON_FHIR_POSTGRES_DB', ''))
OMOP_ON_FHIR_HOST = str(os.getenv('OMOP_ON_FHIR_HOST', ''))

KETOS_HOST = str(os.getenv('KETOS_HOST', ''))
KETOS_DATA_FOLDER = str(os.getenv('KETOS_DATA_FOLDER', '/ketos'))


