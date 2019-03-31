import sys
import re
import json
import requests
from bs4 import BeautifulSoup


URL = 'https://www.unibo.it/it/didattica/corsi-di-studio/?sort=alphabetic'
REGEX_FLAGS = re.MULTILINE
RE_ID = re.compile(r'Codice[\s\\n]+(\d{4})', flags=REGEX_FLAGS)
RE_CAMPUS = re.compile(r'Sede didattica:\s(\w+)', flags=REGEX_FLAGS)
RE_LANG = re.compile(r'Lingua:\s+(\w+)', flags=REGEX_FLAGS)
LANGS = {'italiano': 'it', 'inglese': 'en'}


def match_or_blank(src_html, regex):
    matches = regex.search(str(src_html))
    if matches is None:
        return ''
    if matches.groups()[0] is None:
        return ''
    return matches.groups()[0]


def parse_lang(src_html):
    lang = match_or_blank(src_html, RE_LANG).lower()
    return LANGS[lang] if lang in LANGS else ''


def course_factory(src_html):
    desc = src_html.next_sibling.next_sibling
    return {
        'id': match_or_blank(desc, RE_ID),
        'title': next(src_html.stripped_strings),
        'lang': parse_lang(desc),
        'campus': match_or_blank(desc, RE_CAMPUS),
        'url': desc.find('a', text='Sito del Corso')['href']
    }


def main():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    html_list = soup.select('div.plusminus-results dt.output-list')
    courses = [course_factory(e) for e in html_list]
    courses.sort(key=lambda x: x['title'])
    json.dump(courses, sys.stdout, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
