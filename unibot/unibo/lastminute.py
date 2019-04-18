import logging
import re
from bs4 import BeautifulSoup
from unibot.urlfetch import fetch
from unibot.cache import cache_for


RE_HTML_TR = re.compile(r'(<\/tr>[\w\d\s<>!\-/]*)<td ', flags=re.MULTILINE | re.IGNORECASE)


class News:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __hash__(self):
        return hash((self.title, self.content))

    def __str__(self):
        return "<b>{}</b>\n{}".format(self.title, self.content)


@cache_for(minutes=30)
def get_news(url):
    src = fetch(url)
    soup = BeautifulSoup(fix_html(src.text), 'html.parser')
    news_list = soup.select('#Table13 td.percorso > table > tr > td > table > tr > td:nth-child(2)')
    return [news_factory(n) for n in news_list[1:]]


def news_factory(news):
    strings = list(news.stripped_strings)
    return News(strings[0], strings[1])


def fix_html(src_html):
    # was it that hard to check your code?
    # now I have to add <tr> where they're missing
    return RE_HTML_TR.sub(r'\1 <tr><td ', src_html)
