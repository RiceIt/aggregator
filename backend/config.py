import os


class Configuration:
    DEBUG = True
    SECRET_KEY = '17f5022fc66a716659716c25547fe9911bfc054ac61fb53e2ad0badf3d6c'
    MONGODB_URI = 'mongodb://localhost:27017/'
    USER = os.environ.get('POSTGRESQL_USER')
    PASSWORD = os.environ.get('POSTGRESQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@localhost/aggregator'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
