from datetime import datetime

from backend.app import db


filters = db.Table('filters',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('filter_id', db.Integer, db.ForeignKey('filter.id'), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    psw = db.Column(db.String(50), unique=True)
    filters = db.relationship('Filter', secondary=filters, lazy='subquery', backref=db.backref('users', lazy=True))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.id}"


class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)



