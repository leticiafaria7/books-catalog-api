# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from tqdm import tqdm
from word2number import w2n

from src.extensions import db
from src.models import Book
from config import url_books

# ----------------------------------------------------------------------------------------------- #
# Obter nomes e links das categorias de livros
# ----------------------------------------------------------------------------------------------- #

def get_dict_categories(url_books):

    response = requests.get(url_books)
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

# ----------------------------------------------------------------------------------------------- #
# Obter informações dos livros
# ----------------------------------------------------------------------------------------------- #

def get_books_attrs(url_cat, cat):
    response = requests.get(url_cat)
    soup = BeautifulSoup(response.text, 'html.parser')

    livros_soup = soup.find_all('article')
    dados = []

    for livro in livros_soup:
        title = livro.find('h3').find('a')['title']
        price = float(livro.find_all('p')[1].get_text().replace('Â£', ''))
        rating = int(w2n.word_to_num(livro.find('p')['class'][1].lower()))
        availability = livro.find_all('p')[2].get_text(strip=True)
        image = urljoin(url_books, livro.find('img')['src'])

        dados.append({
            'title': title,
            'price': price,
            'rating': rating,
            'availability': availability,
            'category': cat,
            'image': image
        })

    return dados, soup

# ----------------------------------------------------------------------------------------------- #
# Adicionar cada livro na tabela do banco de dados
# ----------------------------------------------------------------------------------------------- #

def populate_books(url_books):

    if Book.query.first():
        print("Tabela de livros já populada. Ignorando...")

    else:
        categories_links = get_dict_categories(url_books)

        for cat, link in tqdm(categories_links.items()):

            url_cat = url_books + link

            while True:
                dados, soup_cat = get_books_attrs(url_cat, cat)

                for book in dados:
                    exists = Book.query.filter_by(title = book['title'], category = book['category']).first()
                    if exists:
                        continue

                    new_book = Book(**book)

                    db.session.add(new_book)
                    db.session.commit()

                next_button = soup_cat.find('li', class_ = 'next')

                if next_button:
                    next_page = next_button.find('a')['href']
                    url_cat = urljoin(url_cat, next_page)
                else:
                    break

