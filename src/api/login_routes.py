# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

from ..instances import bp, supabase

# ----------------------------------------------------------------------------------------------- #
# Registrar usuário
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/auth/register', methods=['POST'])
def register_user():
    """
    Registra um novo usuário
    ---
    tags:
        - Sistema de autenticação

    consumes:
        - application/json

    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            required:
                - username
                - password
            properties:
                username:
                    type: string
                    example: usuario_123
                password:
                    type: string
                    example: minhaSenha@123

    responses:
        201:
            description: Usuário criado com sucesso
            schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Usuário criado com sucesso

        400:
            description: Erro de validação dos dados
            schema:
                type: object
                properties:
                    error:
                        type: string
            examples:
                username_com_espaco:
                    error: username não pode ter espaço
                username_caracter_especial:
                    error: não pode haver caracteres especiais
                username_curto:
                    error: username deve ter mais de 3 caracteres
                senha_curta:
                    error: senha deve ter mais de 3 caracteres
                campos_obrigatorios:
                    error: Username e senha são obrigatórios

        409:
            description: Nome de usuário já está em uso
            schema:
                type: object
                properties:
                    error:
                        type: string
                        example: Nome de usuário já está em uso

        415:
            description: Tipo de mídia não suportado
            schema:
                type: object
                properties:
                    error:
                        type: string
                        example: Tipo de entrada não suportado

        500:
            description: Erro interno do servidor
            schema:
                type: object
                properties:
                    error:
                        type: string
                        example: Erro interno do servidor
    """
    try:
        # verificar se o input é um json no formato necessário
        if not request.is_json:
            return jsonify({"error": "Tipo de entrada não suportado"}), 415

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        # Campos obrigatórios
        if not username or not password:
            return jsonify({"error": "Username e senha são obrigatórios"}), 400

        # ======================
        # validações do formato do username
        # ======================

        if " " in username:
            return jsonify({"error": "username não pode ter espaço"}), 400

        if len(username) < 3:
            return jsonify({"error": "username deve ter mais de 3 caracteres"}), 400

        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return jsonify({"error": "não pode haver caracteres especiais"}), 400

        # ======================
        # validação do formato da senha
        # ======================

        if len(password) < 3:
            return jsonify({"error": "senha deve ter mais de 3 caracteres"}), 400

        # ======================
        # verificar se o usuário já existe
        # ======================

        existing_user = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
            .execute()
        )

        if existing_user.data:
            return jsonify({"error": "Nome de usuário já está em uso"}), 409

        # ======================
        # criar usuário
        # ======================

        password_hash = generate_password_hash(password)

        supabase.table("users").insert({
            "username": username,
            "password_hash": password_hash
        }).execute()

        return jsonify({"message": "Usuário criado com sucesso"}), 201

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500

# ----------------------------------------------------------------------------------------------- #
# Login de usuário e geração de token de autenticação
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/auth/login', methods=['POST'])
def login():
    """
    Faz login do usuário e retorna um token de acesso JWT
    ---
    tags:
        - Sistema de autenticação

    consumes:
        - application/json

    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            required:
                - username
                - password
            properties:
                username:
                    type: string
                    example: usuario_123
                password:
                    type: string
                    example: minhaSenha@123

    responses:
        200:
            description: Login realizado com sucesso
            schema:
                type: object
                properties:
                    access_token:
                        type: string
                        example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        400:
            description: Erro de validação da requisição
            schema:
                type: object
                properties:
                    error:
                        type: string
            examples:
                campos_obrigatorios:
                    error: Username e senha são obrigatórios
                json_invalido:
                    error: Corpo da requisição inválido

        401:
            description: Credenciais inválidas
            schema:
                type: object
                properties:
                    error:
                        type: string
                        example: Usuário ou senha inválidos

        415:
            description: Tipo de mídia não suportado
            schema:
                type: object
                properties:
                    error:
                        type: string
                        example: Tipo de entrada não suportado

        500:
            description: Erro interno do servidor
            schema:
                type: object
                properties:
                    error:
                        type: string
                        example: Erro interno do servidor
    """
    try:
        # verificar se o input é um json no formato necessário
        if not request.is_json:
            return jsonify({"error": "Tipo de entrada não suportado"}), 415

        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({"error": "Corpo da requisição inválido"}), 400

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

        token = create_access_token(identity=str(user.data["id"]))

        return jsonify({"access_token": token}), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500

# ----------------------------------------------------------------------------------------------- #
# Verificar acesso a rota protegida
# ----------------------------------------------------------------------------------------------- #

@bp.route('/protected', methods = ['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity() # retorna o identity usado na criação do token
    return jsonify({'msg':f"Usuário com ID {current_user_id} acessou a rota protegida"}), 200

# ----------------------------------------------------------------------------------------------- #
# Definir user_id no registro de logs
# ----------------------------------------------------------------------------------------------- #

@bp.route("/profile")
@jwt_required()
def profile():
    g.user_id = get_jwt_identity()
    return {"ok": True}
