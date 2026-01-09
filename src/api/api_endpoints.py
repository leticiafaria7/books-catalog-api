# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify, current_app
import pandas as pd
from datetime import datetime
from ..instances import bp

# ----------------------------------------------------------------------------------------------- #
# Ler a base de dados
# ----------------------------------------------------------------------------------------------- #

df = pd.read_csv('data/base_livros.csv')

# ----------------------------------------------------------------------------------------------- #
# Listar os livros disponíveis na base de dados
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books', methods = ['GET'])

def get_books():
    """
    Lista de livros disponíveis na base
    ---
    tags:
      - Informações dos livros
    responses:
      200:
        description: Dicionário id-título
        schema:
          type: object
          additionalProperties:
            type: string
    """
    dict_books = df.set_index('id')['title'].to_dict()

    return jsonify(dict_books), 200

# ----------------------------------------------------------------------------------------------- #
# Listar todas as categorias de livros disponíveis
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/categories', methods = ['GET'])

def get_categories():
    """
    Lista categorias únicas de livros
    ---
    tags:
      - Informações dos livros
    responses:
      200:
        description: Lista de categorias
        schema:
          type: object
          properties:
            categories:
              type: array
              items:
                type: string
    """
    categories = {'categories': list(df['category'].unique())}
    
    return jsonify(categories), 200

# ----------------------------------------------------------------------------------------------- #
# Retornar detalhes completos de um livro específico pelo ID
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/<int:id>', methods = ['GET'])

def get_book_info(id):
    """
    Retorna detalhes do livro especificado pelo ID
    ---
    tags:
      - Informações dos livros
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: ID do livro 
    responses:
      200:
        description: Detalhes do livro
      404:
        description: Livro não encontrado
    """

    livro = df[df['id'] == id].to_dict(orient = 'records')

    return jsonify(livro), 200

# ----------------------------------------------------------------------------------------------- #
# Buscar livro por título e/ou categoria
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/search', methods = ['GET'])

def get_books_search():
    """
    Busca livros por título ou categoria
    ---
    tags:
      - Informações dos livros
    parameters:
      - in: query
        name: title
        required: false
        schema:
          type: string
        description: Título do livro 
      - in: query
        name: category
        required: false
        schema:
          type: string
        description: Categoria de livros
    responses:
      200:
        description: Lista de livros encontrados
      404:
        description: Não foram encontrados resultados
    """
    title = request.args.get('title')
    category = request.args.get('category')

    df_query = df.copy()

    if title:
        df_query = df_query[df_query['title'].str.lower().str.contains(title.lower())]

    if category:
        df_query = df_query[df_query['category'].str.lower().str.contains(category.lower())]

    return jsonify(df_query.to_dict(orient = 'records')), 200

# ----------------------------------------------------------------------------------------------- #
# Estatísticas gerais da coleção
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/stats/overview', methods = ['GET'])

def get_overview():
    """
    Estatísticas gerais da coleção
    ---
    tags:
      - Stats
    responses:
      200:
        description: Estatísticas gerais da coleção
    """
    dict_overview = {
        'total_books': df.shape[0],
        'mean_price': round(df['price'].mean(), 2),
        'ratings_distribution': df['rating'].value_counts().to_dict()
    }
    
    return jsonify(dict_overview), 200

# ----------------------------------------------------------------------------------------------- #
# Estatísticas por categoria
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/stats/categories', methods = ['GET'])

def get_category_stats():
    """
    Estatísticas de livros agregadas por categoria
    ---
    tags:
      - Stats
    responses:
      200:
        description: Estatísticas por categoria

    """
    lista_stats_cats = (
        df.groupby('category')
        .agg(
            n_books = ('title', 'count'),
            price_min = ('price', 'min'),
            price_max = ('price', 'max'),
            price_mean = ('price', 'mean'),
            rating_mean = ('rating', 'mean')
        )
        .round(2)
        .to_dict(orient='index')
    )

    return jsonify(lista_stats_cats), 200

# ----------------------------------------------------------------------------------------------- #
# Livros com maior avaliação
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/top-rated', methods = ['GET'])

def get_top_rated():
    """
    Livros com maior avaliação
    ---
    tags:
      - Informações dos livros
    responses:
      200:
        description: Lista de livros encontrados
      404:
        description: Não foram encontrados resultados
    """
    books_top_rated = df[df['rating'] == df['rating'].max()].to_dict(orient = 'records')

    return jsonify(books_top_rated), 200

# ----------------------------------------------------------------------------------------------- #
# Filtrar livros dentro de uma faixa de preço específica
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/price-range', methods = ['GET'])

def get_books_price_range():
    """
    Filtra livros dentro de uma faixa de preço
    ---
    tags:
      - Informações dos livros
    parameters:
      - in: query
        name: min
        required: false
        schema:
          type: float
        description: Preço mínimo
      - in: query
        name: max
        required: false
        schema:
          type: float
        description: Preço máximo
    responses:
      200:
        description: Lista de livros encontrados
      404:
        description: Não foram encontrados resultados
      500:
        description: Formato de valor inválido
    
    """
    min_price = request.args.get('min')
    max_price = request.args.get('max')

    def is_float(valor: str) -> bool:
      try:
          float(valor.replace(',', '.'))
          return True
      except (ValueError, TypeError):
          return False

    df_query = df.copy()

    if min_price:
        if is_float(min_price):
          df_query = df_query[df_query['price'] >= float(min_price.replace(',', '.'))]
        else:
            return jsonify({'message': 'Formato de valor inválido'}), 500

    if max_price:
        if is_float(max_price):
          df_query = df_query[df_query['price'] <= float(max_price.replace(',', '.'))]
        else:
            return jsonify({'message': 'Formato de valor inválido'}), 500
    
    if df_query.shape[0] == 0:
        return jsonify({'message': 'Nenhum livro encontrado'}), 404
    
    return jsonify(df_query.to_dict(orient = 'records')), 200

# ----------------------------------------------------------------------------------------------- #
# Verificar status da API e conectividade com os dados
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/health', methods=['GET'])
def get_api_health():
    """
    Verifica o status da API e a disponibilidade dos dados em memória.
    ---
    tags:
      - API Health
    responses:
      200:
        description: API e dependências saudáveis
        content:
          application/json:
            example:
              status: ok
              database: ok
              version: "1.0.0"
              environment: development
      503:
        description: API indisponível ou com dependências falhando
        content:
          application/json:
            example:
              status: degraded
              database: error
              version: "1.0.0"
              environment: development
    """
    health_status = {
        "status": "ok",
        "api": "running",
        "data_loaded": False,
        "rows": 0,
        "checked_at": datetime.utcnow().isoformat() + "Z"
    }

    try:
        if df is not None:
            health_status["rows"] = df.shape[0]
            health_status["data_loaded"] = not df.empty
    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        return jsonify(health_status), 500

    return jsonify(health_status), 200


