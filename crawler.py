import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

NUM = 1
BASE_URLS = [
    "https://habr.com/ru/articles/",
    "https://habr.com/ru/articles/page2/",
    "https://habr.com/ru/articles/page3/",
    "https://habr.com/ru/articles/page4/",
    "https://habr.com/ru/articles/page5/",
]

def clean_html(html):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<link[^>]*?href=["\'].*?\.(css)["\'][^>]*?>', '', html, flags=re.DOTALL)
    html = re.sub(r'href=["\'].*?\.(css|js)["\']', '', html, flags=re.DOTALL)
    html = re.sub(r'src=["\'].*?\.(css|js)["\']', '', html, flags=re.DOTALL)
    return html

def get_text_pages(base_url, max_page):
    resp = requests.get(base_url)
    s = BeautifulSoup(resp.text, 'html.parser')
    div = s.select_one("#app > div > div.tm-layout > main > div > div > div")
    links = []
    for a_tag in div.find_all('a', class_="tm-title__link", href=True):
        href = a_tag['href']
        if not href.endswith(('.css', '.js')):
            full_url = urljoin(base_url, href)
            links.append(full_url)
    unique_links = list(set(links))
    final_links = unique_links[:max_page]

    return final_links

if __name__ == '__main__':
    m_page = 100
    for base_url in BASE_URLS:
        pages = get_text_pages(base_url, m_page)
        for url in get_text_pages(base_url, m_page):
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Ошибка при запросе {url}: {e}")
                continue
            text = clean_html(response.text)
            with open('data/{}.txt'.format(NUM), 'w', encoding='utf-8') as file:
                file.write(text)
            with open('index.txt', 'a', encoding='utf-8') as index:
                index.write('{}. {}\n'.format(NUM, url))
            NUM += 1
