import os

class Config:

    # configurações de segurança
    SECRET_KEY = 'sua_chave_secreta'
    JWT_SECRET_KEY = 'sua_chave_jwt_secreta'

    # caching básico
    CACHE_TYPE = 'simple'

    # título e versão da doc interativa
    SWAGGER = {
        'title': 'API para Consulta de Livros',
        'uiversion': 3
    }

    # definição do banco
    SQLALCHEMY_DATABASE_URI = 'sqlite:///books.db'

    # evitar warnings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
url_books = "https://books.toscrape.com/"