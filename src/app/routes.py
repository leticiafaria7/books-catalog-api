# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User
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

