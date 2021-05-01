import re
import time

import requests
import datetime

from bs4 import BeautifulSoup

from funcs import insert_one_if_not_exist, update_one, add_categories_if_not_exist


def get_soup_from_script(script):
    html = re.search(pattern, script.string)[0][1:-1]
    soup = BeautifulSoup(html, 'lxml')
    return soup


def to_int(created):
    if created.strip() == "":
        return 0
    else:
        return int(created)


def parse_task(_id, url):
    task_html = requests.get(url).text
    # task_pattern = re.compile(r'в сфере(.+)с бюджетом')
    # match = re.search(task_pattern, task_html)
    # categories = [s.strip() for s in match[1].split('/')]
    # print(categories)
    task_soup = BeautifulSoup(task_html, 'lxml')
    task_text = task_soup.find('div', id=f'projectp{_id}')
    categories_tag = task_text.next_sibling.next_sibling.next_sibling.next_sibling
    categories_links = categories_tag.find_all('a')
    categories = [a.string.strip() for a in categories_links]
    unique_categories = list(set(categories))
    return unique_categories


domain = 'https://www.fl.ru'
pattern = re.compile(r"'.+'")

html = requests.get('https://www.fl.ru/projects/?kind=1').content
soup = BeautifulSoup(html, 'lxml')


project_list = soup.find('div', id='projects-list').find_all(class_='b-post')
for project in project_list:
    project: BeautifulSoup
    if 'topprjpay' not in project.attrs['class']:
        title = project.find('h2', class_='b-post__title').find('a').string.strip()
        path = project.find('h2', class_='b-post__title').find('a')['href'].strip()
        _id = project.find('h2', class_='b-post__title').find('a').attrs['name'][3:]
        link = domain + path
        price_script, text_script, foot_script = project('script')
        price_soup = get_soup_from_script(price_script)
        price = price_soup.find('div', class_='b-post__price').text.replace('Безопасная сделка', '').strip()
        text_soup = get_soup_from_script(text_script)
        text = text_soup.find('div', class_='b-post__txt').string.strip()
        foot_soup = get_soup_from_script(foot_script)
        is_task = foot_soup.find('div', class_='b-post__txt').find('span', class_='b-post__bold').string
        strings = foot_soup.find('div', class_='b-post__txt').stripped_strings
        created_ago = list(strings)[-1]
        created_ago = ''.join(list(filter(str.isdigit, created_ago)))
        created_ago_int = to_int(created_ago)
        created_at_full = datetime.datetime.now() - datetime.timedelta(minutes=created_ago_int)
        created_at = created_at_full.strftime("%Y:%m:%d %H:%M")
        exist = insert_one_if_not_exist({'_id': _id, 'title': title, 'link': link, 'price': price, 'text': text, 'created_at': created_at})
        print(title, exist)
        if not exist:
            categories = parse_task(_id, link)
            update_one(_id, categories)
            add_categories_if_not_exist(categories)
        print()
        time.sleep(1)
