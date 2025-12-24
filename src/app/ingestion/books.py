# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
# from IPython.display import Image, display
from tqdm import tqdm
from word2number import w2n

from src.app.extensions import db
from src.app.models import Book

# ----------------------------------------------------------------------------------------------- #
# Instanciar url
# ----------------------------------------------------------------------------------------------- #

url = "https://books.toscrape.com/"

# ----------------------------------------------------------------------------------------------- #
# Obter nomes e links das categorias de livros
# ----------------------------------------------------------------------------------------------- #

def get_dict_categories(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    categories_links = {}

    categories_soup = soup.find_all("a")

    for cat in categories_soup:
        attr = list(cat.attrs.values())[0]

        if attr.startswith("catalogue/category"):
            categories_links[cat.get_text(strip = True)] = attr.replace('index.html', '')

    categories_links.pop('Books')
    # print(f"Quantidade de categorias = {len(categories_links)}")
    return categories_links

categories_links = get_dict_categories(url)

# ----------------------------------------------------------------------------------------------- #
# Obter informações dos livros
# ----------------------------------------------------------------------------------------------- #

def get_books_attrs(url_cat, cat):
    response = requests.get(url_cat)
    soup = BeautifulSoup(response.text, 'html.parser')

    livros_soup = soup.find_all('article')
    # dados = []

    for livro in livros_soup:
        title = livro.find('h3').find('a')['title']
        price = float(livro.find_all('p')[1].get_text().replace('Â£', ''))
        rating = int(w2n.word_to_num(livro.find('p')['class'][1].lower()))
        availability = livro.find_all('p')[2].get_text(strip=True)
        image = urljoin(url, livro.find('img')['src'])

        tmp_dict = {
            'title': title,
            'price': price,
            'rating': rating,
            'availability': availability,
            'category': cat,
            'image': image
        }

    return tmp_dict, soup

for cat, link in tqdm(categories_links.items()):

    url_cat = url + link

    while True:
        tmp_dict, soup_cat = get_books_attrs(url_cat, cat)

        new_book = Book(
            title = tmp_dict['title'],
            price = tmp_dict['price'],
            rating = tmp_dict['rating'],
            availability = tmp_dict['availability'],
            category = tmp_dict['category'],
            image = tmp_dict['image']
        )

        db.session.add(new_book)
        db.session.commit()

        next_button = soup_cat.find('li', class_ = 'next')

        if next_button:
            next_page = next_button.find('a')['href']
            url_cat = urljoin(url_cat, next_page)
        else:
            break