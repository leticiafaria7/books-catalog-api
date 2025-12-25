# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User, Book
from .extensions import db

# ----------------------------------------------------------------------------------------------- #
# Instanciar bp
# ----------------------------------------------------------------------------------------------- #

bp = Blueprint('main', __name__)

# ----------------------------------------------------------------------------------------------- #
# Página inicial
# ----------------------------------------------------------------------------------------------- #

@bp.route('/')

def home():
    return('Página Inicial')

# ----------------------------------------------------------------------------------------------- #
# Registrar usuário
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/auth/register', methods = ['POST'])

def register_user():
    data = request.get_json()
    if User.query.filter_by(username = data['username']).first():
        return jsonify({'error': 'User already exists'}), 400
    
    new_user = User(username = data['username'], password = data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User created'}), 201

# no postman: body > raw > JSON > criar dict com username e password > send

# ----------------------------------------------------------------------------------------------- #
# Login de usuário e geração de token de autenticação
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/auth/login', methods = ['POST'])

def login():
    data = request.get_json()
    user = User.query.filter_by(username = data['username']).first()

    if user and user.password == data['password']:
        token = create_access_token(identity = str(user.id))
        return jsonify({'access_token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# ----------------------------------------------------------------------------------------------- #
# Verificar acesso a rota protegida
# ----------------------------------------------------------------------------------------------- #

@bp.route('/protected', methods = ['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity() # retorna o identity usado na criação do token
    return jsonify({'msg':f"Usuário com ID {current_user_id} acessou a rota protegida"}), 200

# ----------------------------------------------------------------------------------------------- #
# Listar os livros disponíveis na base de dados
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books', methods = ['GET'])

def get_books():
    pass

# ----------------------------------------------------------------------------------------------- #
# Retornar detalhes completos de um livro específico pelo ID
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/<int:book_id>', methods = ['GET'])

def get_book_info():
    pass

# ----------------------------------------------------------------------------------------------- #
# Buscar livro por título e/ou categoria
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/search?title=<string:title>&category=<string:category>', methods = ['GET'])

def get_books_search():
    pass

# ----------------------------------------------------------------------------------------------- #
# Listar todas as categorias de livros disponíveis
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/categories', methods = ['GET'])

def get_categories():
    """
    Lista categorias únicas de livros
    ---
    tags:
      - Books
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
# Verificar status da API e conectividade com os dados
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/health', methods = ['GET'])

def get_api_health():
    pass


