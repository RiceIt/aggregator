import json
import os
import requests

from db.models import get_user_categories, create_or_delete_category, get_times, update_user_time


def send_message(method, chat_id, **kwargs):
    token = os.environ["TOKEN"]
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, **kwargs}
    response = requests.post(url, data=data)


def send_start_message(chat_id):
    keyboard = get_start_buttons()
    reply_markup = json.dumps({"keyboard": keyboard, "resize_keyboard": True}, ensure_ascii=True)
    params = {"text": "Приветствую. Настроить категории - чтобы выбрать желаемые площадки и категории\n\n"
                      "Настроить время - чтобы выбрать тип уведомлений в завсисмости от времени суток",
              "reply_markup": reply_markup}
    send_message("sendMessage", chat_id, **params)


def get_start_buttons():
    return [[{"text": "Настроить категории"}, {"text": "Настроить время"}], ]


def send_platforms_message(chat_id):
    inline_keyboard = get_platforms_buttons()
    reply_markup = json.dumps({"inline_keyboard": inline_keyboard}, ensure_ascii=True)
    params = {"text": "Выбери платформу", "reply_markup": reply_markup}
    send_message("sendMessage", chat_id, **params)


def send_platforms_list(chat_id, message_id):
    inline_keyboard = get_platforms_buttons()
    reply_markup = json.dumps({"inline_keyboard": inline_keyboard})
    params = {"chat_id": chat_id, "message_id": message_id, "text": "Выбери платформу", "reply_markup": reply_markup}
    send_message("editMessageText", **params)


def notifications_message_handler(chat_id):
    inline_keyboard = get_time_buttons(chat_id, 1)
    reply_markup = json.dumps({"inline_keyboard": inline_keyboard}, ensure_ascii=True)
    data = {"text": "Нажимай на кнопки, чтобы настроить каждый промежуток времени.\n"
                    "🟢 - уведомления будут приходить как обычно\n"
                    "🔴 - уведомления отключены\n"
                    "🌑 - уведомления будут приходить, но в беззвучно.",
            "reply_markup": reply_markup}
    send_message("sendMessage", chat_id, **data)


def get_time_buttons(chat_id, page):
    emojis = {
        0: "🌑",
        1: "🟢",
        2: "🔴",
    }
    minutes = {
        0: "00",
        1: "30",
    }
    offset = (page - 1) * 16
    limit = 16
    times = get_times(chat_id, offset, limit)
    inline_keyboard = []
    for i, j in times:
        button = {"text": f"{emojis[j]} {i//2}:{minutes[i%2]}-{(i+1)//2}:{minutes[(i+1)%2]}", "callback_data": f"t:{i}"}
        if i % 2 == 0:
            row = [button, ]
        else:
            row.append(button)
            inline_keyboard.append(row)
        # for j in range(2):
        #     row.append({"text": f"✅ {i + j}:00-{i + j}:30", "callback_data": f"{i + j}"})
        #     row.append({"text": f"✅ {i + j}:30-{i + j + 1}:00", "callback_data": f"{i + j}"})
    inline_keyboard.append([get_previous_time_page(page), get_next_time_page(page)])
    return inline_keyboard


def get_previous_time_page(current_page):
    if current_page > 1:
        return {"text": "◀", "callback_data": f"t:p:{current_page - 1}"}
    else:
        return {"text": " ", "callback_data": f"empty"}


def get_next_time_page(current_page):
    if current_page < 3:
        return {"text": "▶", "callback_data": f"t:p:{current_page + 1}"}
    else:
        return {"text": " ", "callback_data": f"empty"}


def update_time(chat_id, time_hour):
    update_user_time(chat_id, time_hour)


def notifications_callback_handler(chat_id, message_id, page):
    inline_keyboard = get_time_buttons(chat_id, int(page))
    reply_markup = json.dumps({"inline_keyboard": inline_keyboard}, ensure_ascii=True)
    params = {"chat_id": chat_id, "message_id": message_id, "reply_markup": reply_markup}
    send_message("editMessageReplyMarkup", **params)


def update_category(chat_id, message_id, platform, category_id, page, callback_query_id):
    text = create_or_delete_category(chat_id, category_id)
    answer_callback_query(callback_query_id, text=text)
    send_platform_categories_list(chat_id, message_id, platform, page)


def get_platforms_buttons():
    buttons = [
        {"text": "fl.ru", "callback_data": "p:fl.ru:1"},
        {"text": "freelance.ru", "callback_data": "p:freelance.ru:1"},
        {"text": "freelance.habr.com", "callback_data": "p:freelance.habr.com:1"},
        {"text": "weblancer.net", "callback_data": "p:weblancer.net:1"},
        {"text": "freelancehunt.com", "callback_data": "p:freelancehunt.com:1"},
    ]
    inline_keyboard = get_keyboard_button(buttons, 2, 3)
    return inline_keyboard


def get_categories_buttons(chat_id, platform, page):
    offset = (page - 1) * 16
    limit = 32
    user_categories = get_user_categories(platform=platform, chat_id=chat_id, offset=offset, limit=limit)
    page_user_categories = user_categories[:16]
    categories_data = map(lambda category: (f"✅ {category[0]}", category[1]) if category[2] else (category[0], category[1]), page_user_categories)
    categories_names_buttons = [{"text": text, "callback_data": f"c:{platform}:{callback_data}:{page}"} for text, callback_data in categories_data]

    categories_names_buttons_sorted = get_keyboard_button(categories_names_buttons, 2, 8)
    categories_names_buttons_sorted.append(
        [get_previous_page(platform, page), get_back_button(), get_next_page(platform, page, len(user_categories))]
    )
    return categories_names_buttons_sorted


def get_back_button():
    return {"text": "Назад ↩", "callback_data": "start"}


def get_previous_page(platform, current_page):
    if current_page > 1:
        return {"text": "◀", "callback_data": f"p:{platform}:{current_page - 1}"}
    else:
        return {"text": " ", "callback_data": f"empty"}


def get_next_page(platform, current_page, user_categories_length):
    if user_categories_length > 16:
        return {"text": "▶", "callback_data": f"p:{platform}:{current_page + 1}"}
    else:
        return {"text": " ", "callback_data": f"empty"}


def get_keyboard_button(buttons, columns, rows):
    result = []
    row = []
    for i, button in enumerate(buttons):
        if i % columns == 0:
            result.append(row)
            row = [button, ]
        else:
            row.append(button)
    for j in range(columns - len(row)):
        row.append({"text": "                                       ", "callback_data": "empty"})
    result.append(row)
    for k in range(rows + 1 - len(result)):
        result.append([{"text": "                                       ", "callback_data": "empty"} for _ in range(columns)])
    return result


def send_platform_categories_list(chat_id, message_id, platform, page):
    inline_keyboard = get_categories_buttons(chat_id, platform, page)
    reply_markup = json.dumps({"inline_keyboard": inline_keyboard})
    params = {"chat_id": chat_id, "message_id": message_id, "text": "Выбери категорию", "reply_markup": reply_markup}
    send_message("editMessageText", **params)


def answer_callback_query(callback_query_id, **kwargs):
    method = "answerCallbackQuery"
    token = os.getenv("TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"

    data = {"callback_query_id": callback_query_id, **kwargs}
    requests.post(url, data=data)
