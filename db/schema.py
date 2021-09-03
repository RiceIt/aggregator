from datetime import datetime

from sqlalchemy import Table, Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


users_categories = Table(
    "users_categories", Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True),
)


users_times = Table(
    "users_times", Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('time_id', ForeignKey('times.id'), primary_key=True),
    Column('mode', Integer),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    psw = Column(String(255), unique=True)
    categories = relationship('Category', secondary='users_categories', backref="users")
    is_active = Column(Boolean)
    silent_mode = Column(Boolean)
    date = Column(DateTime, default=datetime.utcnow)
    times = relationship('Time', secondary='users_times', backref="users")

    def __repr__(self):
        return self.chat_id


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    slug = Column(String(255))
    platform = Column(String(255))

    __table_args__ = (
        UniqueConstraint('slug', 'platform'),
    )

    def __repr__(self):
        return self.name


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    slug = Column(String(255))
    platform = Column(String(255))
    url = Column(String(1024))

    __table_args__ = (
        UniqueConstraint('slug', 'platform'),
    )

    def __repr__(self):
        return self.slug


class Time(Base):
    __tablename__ = "times"

    id = Column(Integer, primary_key=True)
    hour = Column(Integer)
