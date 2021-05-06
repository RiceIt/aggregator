import requests
from bs4 import BeautifulSoup

from parser.funcs import insert_one_if_not_exist, add_filters_if_not_exist, push_notifications


def parse_freelance():
    domain = 'https://freelance.ru'
    pages = ['https://freelance.ru/project/search', 'https://freelance.ru/project/search?page=2&per-page=25']

    for page in pages:
        html = requests.get(page).content
        soup = BeautifulSoup(html, 'lxml')

        project_list = soup.find('div', id='w1').find_all(class_='box-shadow')
        for project in project_list:
            project: BeautifulSoup
            if 'highlight' not in project.attrs['class']:
                title_tag = project.find('h2', class_='title')
                title = title_tag.attrs['title']
                href = title_tag.find('a').attrs['href']
                _id = href.split('.')[-2].split('-')[-1].strip()
                link = domain + href
                text = project.find('a', class_='description').string.strip()
                raw_date = project.find('span', class_='prop').attrs['title']
                created_at = raw_date.replace('Опубликован ', '').replace(' в ', ' ').replace('-', ':')
                category = project.find('span', class_='specs-list').find('span').string.strip()
                price = project.find('div', class_='cost').string.strip()
                task = {'_id': "2" + _id, 'title': title, 'link': link, 'price': price, 'text': text, 'created_at': created_at,
                        'categories': [category, ], 'platform': 'freelance.ru'}
                exist = insert_one_if_not_exist(task, 'freelance')
                if not exist:
                    add_filters_if_not_exist([category, ], "freelance.ru")
                    push_notifications(task, [category, ])
