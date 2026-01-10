import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
url_books = "https://books.toscrape.com/"

# ----------------------------------------------------------------------------------------------- #
# Classe Config
# ----------------------------------------------------------------------------------------------- #

class Config:

    # configurações de segurança
    SECRET_KEY = os.getenv("SECRET_KEY")

    # caching básico
    CACHE_TYPE = 'simple'

    # título e versão da doc interativa
    SWAGGER = {
        'title': 'API para Consulta de Livros',
        'uiversion': 3
    }

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

