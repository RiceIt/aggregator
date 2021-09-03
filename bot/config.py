import os


class Configuration:
    SECRET_KEY = os.environ["SECRET_KEY"]
    POSTGRESQL_USER = os.environ["POSTGRESQL_USER"]
    POSTGRESQL_PASSWORD = os.environ["POSTGRESQL_PASSWORD"]
    POSTGRESQL_DBNAME = 'aggregator'
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@localhost/{POSTGRESQL_DBNAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOT_URI = os.environ['BOT_URI']
