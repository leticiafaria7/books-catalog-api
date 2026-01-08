# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify, current_app
from sqlalchemy import text, func
from ..instances import db, bp, Book

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
    books = (
        db.session.query(Book.id, Book.title)
        .order_by(Book.id)
        .all()
    )
    
    response = {book_id: title for book_id, title in books}

    return jsonify(response), 200

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
    categories = (
        db.session.query(Book.category)
        .distinct()
        .order_by(Book.category)
        .all()
    )
    
    return jsonify({'categories': [c[0] for c in categories]}), 200

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

    livro = Book.query.get(id)

    if not livro:
        return jsonify({'error': 'Livro não encontrado'}), 404

    return jsonify(
        {
            'id': livro.id,
            'title': livro.title,
            'price': livro.price,
            'rating': livro.rating,
            'availability': livro.availability,
            'category': livro.category,
            'image': livro.image
        }
    ), 200

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

    query = Book.query
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if category:
        query = query.filter(Book.category.ilike(f'%{category}%'))

    books_found = query.all()

    if not books_found:
        return jsonify({'message': 'Nenhum livro encontrado'}), 404
    
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'price': b.price,
            'rating': b.rating,
            'availability': b.availability,
            'category': b.category,
            'image': b.image
        }
        for b in books_found
    ]), 200

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
    total_books = int(db.session.query(func.count(Book.id))[0][0])
    mean_price = round(float(db.session.query(func.avg(Book.price))[0][0]), 2)

    dist_ratings = (
        db.session.query(
            Book.rating.label('rating'),
            func.count(Book.id).label('n_rating')
        )
        .group_by(Book.rating)
        .order_by(Book.rating)
        .all()
    )

    dict_results = {
        'total_books': total_books,
        'mean_price': mean_price,
        'ratings_distribution': dict(dist_ratings)
    }
    
    return jsonify(dict_results), 200


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
        schema:
          type: object
          additionalProperties:
            type: object
            properties:
              n_books:
                type: integer
              min_price:
                type: number
                format: float
              max_price:
                type: number
                format: float
              mean_price:
                type: number
                format: float
              mean_rating:
                type: number
                format: float
    """
    results = (
        db.session.query(
            Book.category.label('category'),
            func.count(Book.id).label('n_books'),
            func.min(Book.price).label('min_price'),
            func.max(Book.price).label('max_price'),
            func.avg(Book.price).label('mean_price'),
            func.avg(Book.rating).label('mean_rating')
        )
        .group_by(Book.category)
        .order_by(Book.category)
        .all()
    )

    response = {
        r.category: {
            'n_books': r.n_books,
            'min_price': float(r.min_price),
            'max_price': float(r.max_price),
            'mean_price': round(float(r.mean_price), 2),
            'mean_rating': round(float(r.mean_rating), 2)
        }
        for r in results
    }

    return jsonify(response), 200

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
    books_top_rated = Book.query.filter(Book.rating == 5).all()

    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'price': b.price,
            'rating': b.rating,
            'availability': b.availability,
            'category': b.category,
            'image': b.image
        }
        for b in books_top_rated
    ]), 200

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
    """
    min_price = request.args.get('min')
    max_price = request.args.get('max')

    query = Book.query
    if min:
        query = query.filter(Book.price >= min_price)
    if max:
        query = query.filter(Book.price <= max_price)

    books_found = query.all()
    
    if not books_found:
        return jsonify({'message': 'Nenhum livro encontrado'}), 404
    
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'price': b.price,
            'rating': b.rating,
            'availability': b.availability,
            'category': b.category,
            'image': b.image
        }
        for b in books_found
    ]), 200

# ----------------------------------------------------------------------------------------------- #
# Verificar status da API e conectividade com os dados
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/health', methods=['GET'])
def get_api_health():
    """
    Verifica o status da API e de suas dependências
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
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'ok'
    except Exception:
        db_status = 'error'

    status_code = 200 if db_status == 'ok' else 503

    return jsonify({
        'status': 'ok' if db_status == 'ok' else 'degraded',
        'database': db_status,
        'version': current_app.config.get('API_VERSION', '1.0.0'),
        'environment': current_app.config.get('ENV', 'development')
    }), status_code


