import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    CLOUD_STORAGE_BUCKET = "YOUR BUCKET NAME"
    GOOGLE_APPLICATION_CREDENTIALS = os.path.join(
        basedir, 'YOUR GOOGLE CREDENTIAL.JSON")


class ProductionConfig(Config):
    DEBUG = False
    APP_PORT = "PORT NUMBER"
    SQLALCHEMY_DATABASE_URI = "DATABASE URL"


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    APP_PORT = "PORT NUMBER"
    SQLALCHEMY_DATABASE_URI = "DATABASE URL"
