import requests
import datetime
from bs4 import BeautifulSoup

from parser.funcs import insert_one_if_not_exist, add_filters_if_not_exist, push_notifications, update_text


def get_date(created_ago):
    digits = get_digits(created_ago)
    if "минут" in created_ago:
        return datetime.datetime.now() - datetime.timedelta(minutes=digits)
    elif "час" in created_ago:
        return datetime.datetime.now() - datetime.timedelta(hours=digits)


def get_digits(string):
    return int(''.join(list(filter(str.isdigit, string))))


def parse_text(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')

    strings = soup.find('div', class_='task__description').stripped_strings
    text = '\n'.join(strings)
    return text


def parse_habr():
    domain = 'https://freelance.habr.com'

    html = requests.get('https://freelance.habr.com/tasks').content
    soup = BeautifulSoup(html, 'lxml')

    project_list = soup.find('ul', id='tasks_list').find_all('li', class_='content-list__item')
    for project in project_list:
        project: BeautifulSoup
        title = project.find('div', class_='task__title').attrs.get('title').strip()
        href = project.find('div', class_='task__title').find('a').attrs.get('href').strip()
        link = domain + href
        _id = href.split('/')[-1]
        created_ago = project.find('span', class_='params__published-at').find('span').string.strip()
        created_at = get_date(created_ago).strftime("%Y:%m:%d %H:%M")
        tags_item = project.find('ul', class_='tags tags_short').find_all('li', class_='tags__item')
        categories = [c.a.string for c in tags_item]
        price = project.find('aside', class_='task__column_price').find('div', class_='task__price-icon').next_sibling.next_element.strip()
        task = {'_id': "3" + _id, 'title': title, 'link': link, 'price': price, 'created_at': created_at,
                'platform': 'freelance.habr.com', 'categories': categories}
        exist = insert_one_if_not_exist(task, 'habr')
        if not exist:
            add_filters_if_not_exist(categories, "freelance.habr.com")
            text = parse_text(link)
            update_text("3" + _id, text, 'habr')
            task = {**task, 'text': text}
            push_notifications(task, categories)
