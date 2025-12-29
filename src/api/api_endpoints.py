# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify, current_app
from sqlalchemy import text
from ..models import Book
from ..extensions import db, bp

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
    
    return {book_id: title for book_id, title in books}

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
    
    return jsonify({'categories': [c[0] for c in categories]})

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
    )

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
    ])

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


