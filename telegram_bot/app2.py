import re
import sys
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, '/home/rais/PycharmProjects/aggregator/')

from parser.funcs import insert_one_if_not_exist_freelance

domain = 'https://freelance.ru'
pattern = re.compile(r"'.+'")

html = requests.get('https://freelance.ru/project/search').content
soup = BeautifulSoup(html, 'lxml')

project_list = soup.find('div', id='w1').find_all(class_='box-shadow')
print(len(project_list))
for project in project_list:
    project: BeautifulSoup
    if 'highlight' not in project.attrs['class']:
        title_tag = project.find('h2', class_='title')
        title = title_tag.attrs['title']
        link = title_tag.find('a').attrs['href']
        text = project.find('a', class_='description').string.strip()
        raw_date = project.find('span', class_='prop').attrs['title']
        created_at = raw_date.replace('Опубликован ', '').replace(' в ', ' ').replace('-', ':')
        category = project.find('span', class_='specs-list').find('span').string.strip()
        price = project.find('div', class_='cost').string.strip()
        task = {'title': title, 'link': link, 'price': price, 'text': text, 'created_at': created_at}
        exist = insert_one_if_not_exist_freelance(task)

        print(title, link)
        print(text)
        print(created_at, category, price)
        print()
