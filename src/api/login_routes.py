# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..instances import db, bp, User

# ----------------------------------------------------------------------------------------------- #
# Registrar usuário
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/auth/register', methods = ['POST'])

def register_user():
    """
    Registra um novo usuário.
    ---
    tags:
        - Sistema de autenticação
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        201:
            description: Usuário criado com sucesso
        400:
            description: Usuário já existe
        415:
            description: Tipo de entrada não suportado
    """
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
    """
    Faz login do usuário e retorna um JWT
    ---
    tags:
        - Sistema de autenticação
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        201:
            description: Login bem sucedido, retorna JWT
        400:
            description: Credenciais inválidas
    """
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