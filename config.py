# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import os

# ----------------------------------------------------------------------------------------------- #
# Definir variáveis
# ----------------------------------------------------------------------------------------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
url_books = "https://books.toscrape.com/"

SUPABASE_URL = 'https://ofxoequhfyfxrhnwbpoh.supabase.co'
SUPABASE_KEY = 'sb_publishable_lxna1eHdsSnLqMD0f_rHEg_sJO1iC0l'

# ----------------------------------------------------------------------------------------------- #
# Classe Config
# ----------------------------------------------------------------------------------------------- #

class Config:

    # configurações de segurança
    SECRET_KEY = 'louvre_key'
    # JWT_SECRET_KEY = 'sua_chave_jwt_secreta'

    # caching básico
    CACHE_TYPE = 'simple'

    # título e versão da doc interativa
    SWAGGER = {
        'title': 'API para Consulta de Livros',
        'uiversion': 3
    }

    # definição do banco
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///books.db'

    # evitar warnings
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

