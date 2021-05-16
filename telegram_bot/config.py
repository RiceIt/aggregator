import os


class Configuration:
    SECRET_KEY = os.environ["SECRET_KEY"]
    MONGODB_URI = 'mongodb://localhost:27017/'
    POSTGRESQL_USER = os.environ["POSTGRESQL_USER"]
    POSTGRESQL_PASSWORD = os.environ["POSTGRESQL_PASSWORD"]
    POSTGRESQL_DBNAME = 'aggregator'
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@localhost/aggregator'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
