from datetime import datetime

from sqlalchemy import Table, Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


users_categories = Table(
    "users_categories", Base.metadata,
    Column('user_id', Integer, ForeignKey('degrees.id')),
    Column('category_id', Integer, ForeignKey('users.id')),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    psw = Column(String(255), unique=True)
    categories = relationship('Category', secondary=users_categories, backref="users")
    is_active = Column(Boolean)
    silent_mode = Column(Boolean)
    date = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    slug = Column(String(255))
    platform = Column(String(255))

    __table_args__ = (
        UniqueConstraint('slug', 'platform'),
    )

