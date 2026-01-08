# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from word2number import w2n
from sqlalchemy.exc import IntegrityError

from src.instances import db, Book

from config import url_books

from typing import List, Dict, Tuple, Any

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

def get_books_attrs(url_cat: str, cat: str) -> Tuple[List[Dict[str, Any]], BeautifulSoup]:
    """
    Extrai os atributos de todos os livros presentes em uma página de categoria específica.

    Realiza o parsing do HTML para coletar título, preço, avaliação, disponibilidade 
    e a URL da imagem de cada livro, organizando-os em uma lista de dicionários.

    Args:
        url_cat (str): URL completa da página da categoria a ser raspada.
        cat (str): Nome da categoria correspondente à URL (usado para rotular os dados).

    Returns:
        Tuple[List[Dict[str, Any]], BeautifulSoup]: Uma tupla contendo:
            - Uma lista de dicionários, onde cada dicionário contém os dados de um livro.
            - O objeto BeautifulSoup da página, permitindo verificações posteriores (ex: paginação).

    Raises:
        requests.exceptions.RequestException: Se houver erro na requisição HTTP.
        ValueError: Se a conversão da avaliação por extenso para número falhar.
    """
    
    # fazer a requisição para a página da categoria
    response = requests.get(url_cat)
    soup = BeautifulSoup(response.text, 'html.parser')

    # localizar todos os elementos <article> (livros da página)
    livros_soup = soup.find_all('article')

    # inicializar lista de livros
    dados = []

    # para cada livro, extrair e transformar os dados solicitados
    for livro in livros_soup:
        title = livro.find('h3').find('a')['title']
        price = float(livro.find_all('p')[1].get_text().replace('Â£', ''))
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

    return dados, soup

# ----------------------------------------------------------------------------------------------- #
# Adicionar cada livro na tabela do banco de dados
# ----------------------------------------------------------------------------------------------- #

def books_count() -> int:
    """
    Utiliza a sessão do SQLAlchemy para executar uma consulta,
    contando apenas os identificadores (IDs) na tabela de livros.

    Returns:
        int: O número total de livros cadastrados na base de dados.
    """

    # executar uma query na coluna ID para obter o total de registros
    return db.session.query(Book.id).count()

def populate_books(url_books: str, target: int = 999) -> None:
    """
    Extrai livros de todas as categorias e popula o banco de dados.

    A função percorre cada categoria do site, extrai os dados dos livros (incluindo
    suporte a paginação) e os salva no banco de dados até que o limite definido
    pelo 'target' seja atingido ou todos os livros sejam processados.

    Args:
        url_books (str): A URL base do catálogo de livros.
        target (int): O número máximo de livros desejados no banco de dados. O padrão é 999.

    Returns:
        None: A função realiza operações de escrita no banco de dados e não retorna valores.

    Note:
        Requer as funções auxiliares `get_dict_categories`, `get_books_attrs` 
        e `books_count`, além do objeto de banco de dados `db` e o modelo `Book`.
    """

    # gerar o dicionário mapeando nomes de categorias aos seus links
    categories_links = get_dict_categories(url_books)

    # iterar por categoria
    for cat, link in tqdm(categories_links.items()):

        # se já tiver todos os livros, interromper a execução
        if books_count() >= target:
            break

        # link completo da categoria
        url_cat = url_books + link

        # loop para gerenciar a paginação da categoria
        while True:

            # obter os dados dos livros e o objeto soup da página atual
            dados, soup_cat = get_books_attrs(url_cat, cat)

            # iterar em cada livro
            for book in dados:

                # verificar novamente se o banco já tem todos os livros
                if books_count() >= target:
                    break

                try:
                    # instanciar um novo objeto Book fazendo o unpacking (**) do dicionário e salvar no banco
                    db.session.add(Book(**book))
                    db.session.commit()
                except IntegrityError:
                    # se o livro já existir, desfazer a transação e ignorar
                    db.session.rollback()
                    continue

            # verificar se há um botão "next" na página
            next_button = soup_cat.find('li', class_='next')

            if next_button and books_count() < target:
                # se tiver, pegar o link da próxima página
                next_page = next_button.find('a')['href']
                url_cat = urljoin(url_cat, next_page)
            else:
                # se não houver mais páginas, sai do loop "while" da categoria
                break