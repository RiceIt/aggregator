import re
import requests
import datetime

from bs4 import BeautifulSoup

from funcs import insert_one_if_not_exist


def get_soup_from_script(script):
    html = re.search(pattern, script.string)[0][1:-1]
    soup = BeautifulSoup(html, 'lxml')
    return soup


def to_int(created):
    if created.strip() == "Только что":
        return 0
    else:
        return int(created)


domain = 'https://www.fl.ru'
pattern = re.compile(r"'.+'")

html = requests.get('https://www.fl.ru/projects/?kind=1').content
soup = BeautifulSoup(html, 'lxml')


project_list = soup.find('div', id='projects-list').find_all(class_='b-post')
for project in project_list:
    project: BeautifulSoup
    if 'topprjpay' not in project.attrs['class']:
        title = project.find('h2', class_='b-post__title').find('a').string
        path = project.find('h2', class_='b-post__title').find('a')['href']
        _id = project.find('h2', class_='b-post__title').find('a').attrs['name'][3:]
        link = domain + path
        print(title)
        print(link)
        print(_id)
        price_script, text_script, foot_script = project('script')
        price_soup = get_soup_from_script(price_script)
        price = price_soup.find('div', class_='b-post__price').text.replace('Безопасная сделка', '').strip()
        print(price)
        text_soup = get_soup_from_script(text_script)
        text = text_soup.find('div', class_='b-post__txt').string.strip()
        print(text)
        foot_soup = get_soup_from_script(foot_script)
        is_task = foot_soup.find('div', class_='b-post__txt').find('span', class_='b-post__bold').string
        strings = foot_soup.find('div', class_='b-post__txt').stripped_strings
        print(is_task)
        created_ago = list(strings)[-1]
        print(created_ago)
        created_ago = ''.join(list(filter(str.isdigit, created_ago)))
        created_ago_int = to_int(created_ago)
        print(created_ago, "minutes")
        created_at_full = datetime.datetime.now() - datetime.timedelta(minutes=created_ago_int)
        created_at = created_at_full.strftime("%Y:%m:%d %H:%M")
        print(created_at)
        _ = insert_one_if_not_exist({'_id': _id, 'title': title, 'link': link, 'price': price, 'text': text, 'created_at': created_at})
        print(_)
        print()
