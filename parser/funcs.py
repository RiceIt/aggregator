import datetime

from loguru import logger


from db.models import add_task, add_category_if_not_exists, get_users
from parser.parsers import AbstractBuilder, FlBuilder, FreelanceBuilder, HabrBuilder, WeblancerBuilder, FreelancehuntBuilder
from bot.funcs import send_message


def get_time_code():
    now = datetime.datetime.now().time()
    time_code = now.hour * 2 + now.minute // 30
    return time_code


def push_notifications(task, time_code):
    message = f"📌 <b>{task['title']}</b>\n\n📝 {task['description']}\n\n💰 {task['price']}\n\n" \
              f"📚 {' '.join(task['categories'])}\n\n🔗 {task['url']}"
    users = get_users(task['categories'], task['platform'], time_code)
    for user in users:
        chat_id, mode = user
        if mode == 0:
            send_message("sendMessage", chat_id, text=message, parse_mode='html', disable_notification=True)
        elif mode == 1:
            send_message("sendMessage", chat_id, text=message, parse_mode='html')


def create_task_if_not_exists(builder: AbstractBuilder):
    builder.add_slug()
    builder.add_platform()
    exists = builder.exists()
    if exists:
        return False, None
    builder.add_title()
    builder.add_url()
    builder.add_description()
    builder.add_created_at()
    builder.add_price()
    builder.add_categories()
    return True, builder.task


def main():
    time_code = get_time_code()
    platforms = (
        FlBuilder,
        FreelanceBuilder,
        HabrBuilder,
        WeblancerBuilder,
        FreelancehuntBuilder,
    )

    for platform in platforms:
        tasks_soup_list = platform.get_tasks_list()
        for task_soup in tasks_soup_list:
            created, task = create_task_if_not_exists(platform(task_soup))
            if created:
                add_task(task["slug"], task["platform"], task["url"])
                for category in task["categories"]:
                    add_category_if_not_exists(category, task["platform"])
                push_notifications(task, time_code)
