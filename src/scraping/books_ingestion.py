# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import requests
import pandas as pd
import pytz
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from word2number import w2n
from datetime import datetime
from typing import Dict, Tuple

import sys
from pathlib import Path

# adicionar o caminho da pasta raiz
PROJECT_ROOT = Path().resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import url_books

# ----------------------------------------------------------------------------------------------- #
# Função para printar o horário da execução
# ----------------------------------------------------------------------------------------------- #

def horario_atual(texto = "Término da execução", gap = 0):

    hora_atual = datetime.now(pytz.timezone("America/Sao_Paulo"))
    print(f"{texto.ljust(gap)}: {hora_atual.strftime('%d/%m/%Y %H:%M:%S')}")

# ----------------------------------------------------------------------------------------------- #
# Obter nomes e links das categorias de livros
# ----------------------------------------------------------------------------------------------- #

def get_dict_categories(url_books: str) -> Dict[str, str]:
    """
    Extrai categorias de livros e seus respectivos links a partir de uma URL.

    Realiza uma requisição HTTP para a página informada, analisa o HTML em busca 
    de links que pertençam à estrutura de categorias e organiza os resultados 
    em um dicionário, removendo a categoria genérica 'Books'.

    Args:
        url_books (str): A URL da página principal que contém a lista de categorias.

    Returns:
        Dict[str, str]: Um dicionário onde as chaves são os nomes das categorias 
            (ex: 'Travel') e os valores são os sufixos dos caminhos das URLs 
            (ex: 'catalogue/category/books/travel_2/').

    Raises:
        requests.exceptions.RequestException: Se houver falha na conexão com a URL.
        AttributeError: Se a estrutura do HTML não contiver os atributos esperados.
    """

    # fazer a requisição para obter o conteúdo da página e transformar o conteúdo HTML em um objeto BeautifulSoup para navegação
    response = requests.get(url_books)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    # inicializar dicionário {categoria:link}
    categories_links = {}

    # localizar todos os elementos de âncora (links) no documento
    categories_soup = soup.find_all("a")

    for cat in categories_soup:
        # pegar o primeiro atributo da tag (href)
        attr = list(cat.attrs.values())[0]

        # pegar apenas os links de categorias e armazenar no dicionário o texto como chave e o link como valor
        if attr.startswith("catalogue/category"):
            categories_links[cat.get_text(strip = True)] = attr.replace('index.html', '')

    # remover o link de "books" (que tem todos os livros -> queremos ir salvando por categoria)
    categories_links.pop('Books')
    return categories_links

# ----------------------------------------------------------------------------------------------- #
# Obter informações dos livros
# ----------------------------------------------------------------------------------------------- #

def get_books_attrs(url_cat: str, cat: str) -> Tuple[pd.DataFrame, BeautifulSoup]:
    """
    Extrai os atributos de todos os livros presentes em uma página de categoria específica.

    A função realiza uma requisição HTTP para a URL da categoria informada,
    faz o parsing do HTML retornado e coleta informações relevantes de cada livro
    listado na página. Os dados extraídos incluem título, preço, avaliação,
    disponibilidade, categoria e URL da imagem. Ao final, os dados são organizados
    em um DataFrame do pandas para facilitar análises posteriores.

    Args:
        url_cat (str): URL completa da página da categoria a ser raspada.
        cat (str): Nome da categoria correspondente à URL (usado para rotular os dados).

    Returns:
        Tuple[pd.DataFrame, BeautifulSoup]:
            Uma tupla contendo:
            - pd.DataFrame: DataFrame onde cada linha representa um livro e
              cada coluna representa um atributo extraído (título, preço,
              avaliação, disponibilidade, categoria e imagem).
            - BeautifulSoup: Objeto BeautifulSoup correspondente ao HTML da
              página, útil para verificações adicionais como paginação.

    Raises:
        requests.exceptions.RequestException: Se houver erro na requisição HTTP.
        ValueError: Se a conversão da avaliação por extenso para número falhar.
    """
    
    # fazer a requisição para a página da categoria
    response = requests.get(url_cat)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    # localizar todos os elementos <article> (livros da página)
    livros_soup = soup.find_all('article')

    # inicializar lista de livros
    dados = []

    # para cada livro, extrair e transformar os dados solicitados
    for livro in livros_soup:
        title = livro.find('h3').find('a')['title']
        price = float(livro.find_all('p')[1].get_text().replace('£', ''))
        rating = int(w2n.word_to_num(livro.find('p')['class'][1].lower()))
        availability = livro.find_all('p')[2].get_text(strip=True)
        image = urljoin(url_books, livro.find('img')['src'])

        # consolidar dados em um dicionário
        dados.append({
            'title': title,
            'price': price,
            'rating': rating,
            'availability': availability,
            'category': cat,
            'image': image
        })

    return pd.DataFrame(dados), soup

# ----------------------------------------------------------------------------------------------- #
# Adicionar cada livro na tabela do banco de dados
# ----------------------------------------------------------------------------------------------- #

def populate_books(url_books: str) -> pd.DataFrame:
    """
    Extrai livros de todas as categorias e consolida os dados em uma base única.

    A função percorre todas as categorias disponíveis no catálogo de livros,
    acessando cada página de categoria e tratando a paginação quando existente.
    Para cada página, os dados dos livros são extraídos e acumulados em um
    DataFrame único, que ao final contém todos os livros encontrados no site.

    Args:
        url_books (str):
            URL base do catálogo de livros, utilizada para montar os links
            completos das categorias e páginas subsequentes.

    Returns:
        pd.DataFrame:
            DataFrame contendo todos os livros extraídos de todas as categorias,
            com seus respectivos atributos (título, preço, avaliação,
            disponibilidade, categoria e imagem).

    Note:
        Esta função depende das seguintes funções e objetos auxiliares:
        - get_dict_categories: para obter o mapeamento entre categorias e seus links.
        - get_books_attrs: para extrair os atributos dos livros de cada página.
        - tqdm: para exibir a barra de progresso durante a iteração.
    """
    gap = 70
    horario_atual('Início da execução', gap = gap)
    base_livros = pd.DataFrame()

    # gerar o dicionário mapeando nomes de categorias aos seus links
    horario_atual("Obtendo o dicionário das categorias e respectivos links", gap = gap)
    print()
    categories_links = get_dict_categories(url_books)

    # iterar por categoria
    horario_atual("Iterando as categorias para obter os dados dos livros", gap = gap)
    for cat, link in tqdm(categories_links.items()):

        # link completo da categoria
        url_cat = url_books + link

        # Loop para tratar a paginação dentro de cada categoria
        while True:
            # Extrai os dados dos livros da página atual e o HTML parseado
            tmp, soup_cat = get_books_attrs(url_cat, cat)

            # Concatena os dados extraídos ao DataFrame principal
            base_livros = pd.concat(
                [base_livros, tmp],
                ignore_index=True
            )

            # Verifica a existência do botão de próxima página
            next_button = soup_cat.find('li', class_='next')

            if next_button:
                # Caso exista, extrai o link da próxima página
                next_page = next_button.find('a')['href']

                # Atualiza a URL da categoria para apontar para a próxima página
                url_cat = urljoin(url_cat, next_page)
            else:
                # Encerra o loop quando não há mais páginas na categoria
                break

    horario_atual('Término do loop', gap = gap)
    print()
    print(f"Tamanho da base de dados: {base_livros.shape[0]}")

    # remover livros duplicados
    base_livros = base_livros.drop_duplicates(subset = 'title').reset_index(drop = True)

    # criar coluna de id
    base_livros = base_livros.reset_index(names = 'id').assign(id = lambda df: df['id'] + 1)

    # salvar base de dados
    base_livros.to_csv('../../data/base_livros.csv', index = False)
    horario_atual('Base de dados salva', gap = gap)
    print()
