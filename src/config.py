import os

POSTGRES_USER = str(os.getenv('POSTGRES_USER', ''))
POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD', ''))
POSTGRES_DB = str(os.getenv('POSTGRES_DB', ''))

DOCKER_REGISTRY_USERNAME = str(os.getenv('DOCKER_REGISTRY_USERNAME', ''))
DOCKER_REGISTRY_PASSWORD = str(os.getenv('DOCKER_REGISTRY_PASSWORD', ''))
DOCKER_REGISTRY_URL = str(os.getenv('DOCKER_REGISTRY_URL', ''))
DOCKER_REGISTRY_DOMAIN = str(os.getenv('DOCKER_REGISTRY_DOMAIN', ''))

ML_SERVICE_ADMIN_USERNAME = str(os.getenv('ML_SERVICE_ADMIN_USERNAME', ''))
ML_SERVICE_ADMIN_EMAIL = str(os.getenv('ML_SERVICE_ADMIN_EMAIL', ''))
ML_SERVICE_ADMIN_PASSWORD = str(os.getenv('ML_SERVICE_ADMIN_PASSWORD', ''))

PROJECT_NAME = str(os.getenv('PROJECT_NAME', ''))
