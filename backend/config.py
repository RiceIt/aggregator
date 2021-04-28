import os


class Configuration:
    DEBUG = True
    MONGODB_URI = 'mongodb://localhost:27017/'
    USER = os.environ.get('POSTGRESQL_USER')
    PASSWORD = os.environ.get('POSTGRESQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@localhost/aggregator'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
