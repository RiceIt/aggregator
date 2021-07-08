from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Configuration

engine = create_engine(Configuration.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(engine, future=True)


db = SQLAlchemy()
migrate = Migrate()

user_filters = db.Table('user_filters',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('filter_id', db.Integer, db.ForeignKey('filters.id'), primary_key=True),
)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True)
    psw = db.Column(db.String(255), unique=True)
    filters = db.relationship('Filters', secondary=user_filters, lazy='subquery', backref=db.backref('users', lazy=True))
    is_active = db.Column(db.Boolean)
    silent_mode = db.Column(db.Boolean)
    adding_filters = db.Column(db.Boolean)
    current_platform = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.id}"


class Filters(db.Model):
    __table_args__ = (db.UniqueConstraint('slug', 'platform'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    platform = db.Column(db.String(255))
