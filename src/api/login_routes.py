# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash

from ..instances import bp
from config_keys import SUPABASE_KEY, SUPABASE_URL

# configurações da supabase (para armazenar os logins)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username e senha são obrigatórios"}), 400

    # Verifica se usuário já existe
    existing_user = (
        supabase
        .table("users")
        .select("id")
        .eq("username", username)
        .execute()
    )

    if existing_user.data:
        return jsonify({"error": "Nome de usuário já está em uso"}), 409

    password_hash = generate_password_hash(password)

    result = (
        supabase
        .table("users")
        .insert({
            "username": username,
            "password_hash": password_hash
        })
        .execute()
    )

    return jsonify({"message": "Usuário criado com sucesso"}), 201

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
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username e senha são obrigatórios"}), 400

    user = (
        supabase
        .table("users")
        .select("id, password_hash")
        .eq("username", username)
        .single()
        .execute()
    )

    if not user.data:
        return jsonify({"error": "Usuário ou senha inválidos"}), 401

    if not check_password_hash(user.data["password_hash"], password):
        return jsonify({"error": "Usuário ou senha inválidos"}), 401

    token = create_access_token(identity = str(user.data["id"]))

    return jsonify({"access_token": token}), 200

# ----------------------------------------------------------------------------------------------- #
# Verificar acesso a rota protegida
# ----------------------------------------------------------------------------------------------- #

@bp.route('/protected', methods = ['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity() # retorna o identity usado na criação do token
    return jsonify({'msg':f"Usuário com ID {current_user_id} acessou a rota protegida"}), 200