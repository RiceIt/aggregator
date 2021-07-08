import re
import abc
import requests
import datetime

from bs4 import BeautifulSoup

from parser.funcs import is_id_exists, insert_one, push_notifications


class AbstractBuilder(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def get_tasks_list(cls, soup: BeautifulSoup) -> tuple:
        pass

    @abc.abstractmethod
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    @abc.abstractmethod
    def add_platform(self):
        self.platform = self.soup[7]

    @abc.abstractmethod
    def add_id(self):
        self._id = self.soup[0]

    @abc.abstractmethod
    def exists(self) -> bool:
        return is_id_exists(self.platform, self._id)

    @abc.abstractmethod
    def add_title(self):
        self.title = self.soup[1]

    @abc.abstractmethod
    def add_description(self):
        self.description = self.soup[2]

    @abc.abstractmethod
    def add_url(self):
        self.url = self.soup[3]

    @abc.abstractmethod
    def add_created_at(self):
        self.created_at = self.soup[4]

    @abc.abstractmethod
    def add_price(self):
        self.price = self.soup[5]

    @abc.abstractmethod
    def add_categories(self):
        self.categories = self.soup[6]

    @property
    def task(self) -> dict:
        fields = self.__dict__
        del fields["soup"]
        return fields


class FlBuilder(AbstractBuilder):
    PLATFORM = "fl.ru"
    URL = "https://www.fl.ru/projects/?kind=1"

    @classmethod
    def get_task_list(cls) -> tuple:
        html = requests.get(cls.URL).content
        soup = BeautifulSoup(html, 'lxml')
        task_list = soup.find('div', id='projects-list').find_all(class_='b-post')
        return tuple(filter(lambda t: 'topprjpay' not in t.attrs['class'], task_list))

    @staticmethod
    def get_soup_from_script(script):
        pattern = re.compile(r"'.+'")
        html = re.search(pattern, script.string)[0][1:-1]
        soup = BeautifulSoup(html, 'lxml')
        return soup

    @staticmethod
    def to_int(string: str):
        if string.strip() == "":
            return 0
        else:
            return int(string)

    @staticmethod
    def parse_task(_id, url):
        task_html = requests.get(url).text
        task_soup = BeautifulSoup(task_html, 'lxml')
        task_text = task_soup.find('div', id=f'projectp{_id}')
        categories_tag = task_text.next_sibling.next_sibling.next_sibling.next_sibling
        categories_links = categories_tag.find_all('a')
        categories = [a.string.strip() for a in categories_links]
        unique_categories = list(set(categories))
        return unique_categories

    def __init__(self, soup: BeautifulSoup):
        super().__init__(soup)

    def add_id(self):
        self._id = self.soup.find('h2', class_='b-post__title').find('a').attrs['name'][3:]

    def add_platform(self):
        self.platform = "fl.ru"

    def exists(self) -> bool:
        return super().exists()

    def add_title(self):
        try:
            self.title = self.soup.find('h2', class_='b-post__title').find('a').string.strip()
        except AttributeError:
            self.title = ""

    def add_url(self):
        href = self.soup.find('h2', class_='b-post__title').find('a')['href'].strip()
        domain = "https://www.fl.ru"
        self.url = domain + href

    def add_description(self):
        price_script, text_script, foot_script = self.soup('script')
        text_soup = self.get_soup_from_script(text_script)
        self.description = text_soup.find('div', class_='b-post__txt').string.strip()

    def add_created_at(self):
        price_script, text_script, foot_script = self.soup('script')
        foot_soup = self.get_soup_from_script(foot_script)
        strings = foot_soup.find('div', class_='b-post__txt').stripped_strings
        created_ago = list(strings)[-1]
        created_ago = ''.join(list(filter(str.isdigit, created_ago)))
        created_ago_int = self.to_int(created_ago)
        created_at_full = datetime.datetime.now() - datetime.timedelta(minutes=created_ago_int)
        self.created_at = created_at_full.strftime("%Y:%m:%d %H:%M")

    def add_price(self):
        price_script, text_script, foot_script = self.soup('script')
        price_soup = self.get_soup_from_script(price_script)
        self.price = price_soup.find('div', class_='b-post__price').text.replace('Безопасная сделка', '').strip()

    def add_categories(self):
        self.categories = self.parse_task(self._id, self.url)


class FreelanceBuilder(AbstractBuilder):
    PLATFORM = "freelance.ru"
    URLS = ["https://freelance.ru/project/search", "https://freelance.ru/project/search?page=2&per-page=25"]

    @classmethod
    def get_task_list(cls) -> tuple:
        task_list = []
        for url in cls.URLS:
            html = requests.get(url).content
            soup = BeautifulSoup(html, 'lxml')
            task_list.extend(soup.find('div', id='w1').find_all(class_='box-shadow'))
        return tuple(filter(lambda t: 'highlight' not in t.attrs['class'], task_list))

    def __init__(self, soup: BeautifulSoup):
        super().__init__(soup)

    def add_id(self):
        self._id = self.soup.find('h2', class_='title').find('a').attrs['href'].split('.')[-2].split('-')[-1].strip()

    def add_platform(self):
        self.platform = "freelance.ru"

    def exists(self) -> bool:
        return super().exists()

    def add_title(self):
        self.title = self.soup.find('h2', class_='title').attrs['title']

    def add_url(self):
        href = self.soup.find('h2', class_='title').find('a').attrs['href']
        domain = "https://freelance.ru"
        self.url = domain + href

    def add_description(self):
        self.description = self.soup.find('a', class_='description').string.strip()

    def add_created_at(self):
        raw_date = self.soup.find('span', class_='prop').attrs['title']
        self.created_at = raw_date.replace('Опубликован ', '').replace(' в ', ' ').replace('-', ':')

    def add_price(self):
        self.price = self.soup.find('div', class_='cost').string.strip()

    def add_categories(self):
        category = self.soup.find('span', class_='specs-list').find('span').string.strip()
        self.categories = (category,)


class HabrBuilder(AbstractBuilder):
    PLATFORM = "habr.com"

    @classmethod
    def get_task_list(cls) -> tuple:
        urls = {
            "development": "https://freelance.habr.com/tasks?categories=development_all_inclusive,development_backend,development_frontend,development_prototyping,development_ios,development_android,development_desktop,development_bots,development_games,development_1c_dev,development_scripts,development_voice_interfaces,development_other",
            "testing": "https://freelance.habr.com/tasks?categories=testing_sites,testing_mobile,testing_software",
            "admin": "https://freelance.habr.com/tasks?categories=admin_servers,admin_network,admin_databases,admin_security,admin_other",
            "design": "https://freelance.habr.com/tasks?categories=design_sites,design_landings,design_logos,design_illustrations,design_mobile,design_icons,design_polygraphy,design_banners,design_graphics,design_corporate_identity,design_presentations,design_modeling,design_animation,design_photo,design_other",
            "content": "https://freelance.habr.com/tasks?categories=content_copywriting,content_rewriting,content_audio,content_article,content_scenarios,content_naming,content_correction,content_translations,content_coursework,content_specification,content_management,content_other",
            "marketing": "https://freelance.habr.com/tasks?categories=marketing_smm,marketing_seo,marketing_context,marketing_email,marketing_research,marketing_sales,marketing_pr,marketing_other",
            "other": "https://freelance.habr.com/tasks?categories=other_audit_analytics,other_consulting,other_jurisprudence,other_accounting,other_audio,other_video,other_engineering,other_other",
        }
        tasks_soup_list = []
        for category, url in urls.items():
            r = requests.get(url).text
            soup = BeautifulSoup(r, "lxml")
            category_tasks_soup_list = soup.find('ul', id='tasks_list').find_all('li', class_='content-list__item')
            for tasks_soup in category_tasks_soup_list:
                new_tag = soup.new_tag("div", attrs={"id": "category", "category_id": category})
                tasks_soup.append(new_tag)
                tasks_soup_list.append(tasks_soup)
        return tuple(tasks_soup_list)

    @staticmethod
    def get_date(string):
        digits = int(''.join(list(filter(str.isdigit, string))))
        if "минут" in string:
            return datetime.datetime.now() - datetime.timedelta(minutes=digits)
        elif "час" in string:
            return datetime.datetime.now() - datetime.timedelta(hours=digits)
        elif "день" in string or "дня" in string or "дней" in string:
            return datetime.datetime.now() - datetime.timedelta(days=digits)

    @staticmethod
    def parse_text(url):
        html = requests.get(url).content
        soup = BeautifulSoup(html, 'lxml')
        strings = soup.find('div', class_='task__description').stripped_strings
        description = '\n'.join(strings)
        return description

    def __init__(self, soup):
        super().__init__(soup)

    def add_id(self):
        self._id = self.soup.find('div', class_='task__title').find('a').attrs.get('href').strip().split('/')[-1]

    def add_platform(self):
        self.platform = "freelance.habr.com"

    def exists(self) -> bool:
        return super().exists()

    def add_title(self):
        self.title = self.soup.find('div', class_='task__title').attrs.get('title').strip()

    def add_url(self):
        href = self.soup.find('div', class_='task__title').find('a').attrs.get('href').strip()
        domain = "https://freelance.habr.com"
        self.url = domain + href

    def add_description(self):
        self.description = self.parse_text(self.url)

    def add_created_at(self):
        created_ago = self.soup.find('span', class_='params__published-at').find('span').string.strip()
        self.created_at = self.get_date(created_ago).strftime("%Y:%m:%d %H:%M")

    def add_price(self):
        self.price = self.soup.find('aside', class_='task__column_price').find('div',
                                                                               class_='task__price-icon').next_sibling.next_element.strip()

    def add_categories(self):
        self.categories = ("freelance.habr.com",)
