import slugify
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from db.schema import User, Category, Order, users_categories, Time, users_times
from bot.config import Configuration


logger.add("parser.log", format="{time} {level} {message}", level="INFO", rotation="1 week")
engine = create_engine(Configuration.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(engine, future=True)


def get_users(categories, platform, time_code):
    with Session() as session:
        # users = session.query(User.chat_id, User.silent_mode).join(
        #     users_categories, users_categories.c.user_id == User.id).join(
        #     Category, users_categories.c.category_id == Category.id).filter(
        #     User.is_active == True).filter(
        #     Category.name.in_(categories)).filter(
        #     Category.platform == platform).group_by(
        #     User.id, User.silent_mode)

        users = session.query(User.chat_id, users_times.c.mode).join(
            users_categories, users_categories.c.user_id == User.id).join(
            Category, users_categories.c.category_id == Category.id).join(
            users_times, User.id == users_times.c.user_id).join(
            Time, users_times.c.time_id == Time.id).filter(
            Category.name.in_(categories)).filter(
            Category.platform == platform).filter(
            Time.hour == time_code).group_by(
            User.id, users_times.c.mode, Time.hour)

        users = users.all()
        return users


def add_category_if_not_exists(category, platform):
    with Session() as session:
        slug = slugify.slugify(category)
        category = Category(name=category, slug=slug, platform=platform)
        try:
            session.add(category)
            session.commit()
            logger.info(f"На платформе [{platform}] добавлена новая категория [{category.name}]")
        except IntegrityError:
            pass


def is_exists(slug, platform):
    with Session() as session:
        order = session.query(Order).filter_by(slug=slug, platform=platform).first()
        if order:
            return True
        else:
            return False


def add_task(slug, platform, url):
    with Session() as session:
        order = Order(slug=slug, platform=platform, url=url)
        session.add(order)
        session.commit()
        logger.info(f"Задача [{order.url}] успешно добавлена")


def add_user(chat_id):
    with Session() as session:
        try:
            user = User(chat_id=chat_id)
            session.add(user)
            session.commit()
            return user.id
        except IntegrityError:
            pass


def create_times(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        times = session.query(Time).all()
        user.times.extend(times)
        session.commit()
        session.query(users_times).filter(
            users_times.c.user_id == user_id).update({"mode": 1})
        session.commit()


def get_user(chat_id):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=chat_id).first()
        return user


def get_categories(platform):
    with Session() as session:
        categories = session.query(Category.name, Category.slug).filter_by(platform=platform).all()
        return categories


def get_user_categories(platform, chat_id, offset, limit):
    # with Session() as session:
    #     user_categories = session.query(Category.name, Category.slug).filter_by(platform=platform).filter(Category.users.contains(user)).all()
    #     return user_categories
    with Session() as session:
        user_followed_categories_ids = session.query(User.id, users_categories.c.category_id, User.chat_id).join(
            users_categories, User.id == users_categories.c.user_id).filter(
            User.chat_id == chat_id).cte()
        user_categories = session.query(Category.name, Category.id, user_followed_categories_ids.c.chat_id).outerjoin(
            user_followed_categories_ids, user_followed_categories_ids.c.category_id == Category.id).filter(
            Category.platform == platform).order_by(
            Category.name).offset(offset).limit(limit)


        # user_categories = session.query(Category.name, Category.id, User.chat_id).join(
        #     users_categories, users_categories.c.category_id == Category.id).outerjoin(
        #     User, users_categories.c.user_id == User.id).filter(
        #     Category.platform == platform).filter(
        #     (User.chat_id == chat_id) | (User.chat_id == None)).order_by(
        #     Category.name).offset(offset).limit(limit)
        user_categories = user_categories.all()
        return user_categories


def create_or_delete_category(chat_id, category_id):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=chat_id).first()
        user_categories = user.categories
        category = session.query(Category).filter_by(id=category_id).first()
        if category in user_categories:
            user.categories.remove(category)
            session.commit()
            return f'Ты отписался от категории [{category.name}]'
        else:
            user.categories.append(category)
            session.commit()
            return f'Ты подписался на категорию [{category.name}]'


def get_times(chat_id, offset, limit):
    with Session() as session:
        times = session.query(Time.hour, users_times.c.mode).join(
            users_times, Time.id == users_times.c.time_id).join(
            User, users_times.c.user_id == User.id).filter(
            User.chat_id == chat_id).order_by(Time.hour).offset(offset).limit(limit).all()
        return times


def update_user_time(chat_id, time_hour):
    rule = {
        0: 1,
        1: 2,
        2: 0,
    }
    with Session() as session:
        user_time = session.query(users_times.c.user_id, users_times.c.time_id, users_times.c.mode).join(
            User, users_times.c.user_id == User.id).join(
            Time, users_times.c.time_id == Time.id).filter(
            User.chat_id == chat_id).filter(
            Time.hour == time_hour).first()
        session.query(users_times).filter(
            users_times.c.user_id == user_time[0]).filter(
            users_times.c.time_id == user_time[1]).update({"mode": rule[user_time.mode]})
        session.commit()
