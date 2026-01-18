# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import request, jsonify
from flask_jwt_extended import jwt_required
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from ..instances import bp, supabase, jwt

# ----------------------------------------------------------------------------------------------- #
# Ler a base de dados
# ----------------------------------------------------------------------------------------------- #

df = pd.read_csv('data/base_livros.csv')

# ----------------------------------------------------------------------------------------------- #
# Listar os livros disponíveis na base de dados
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books', methods=['GET'])
@jwt_required()
def get_books():
    """
    Lista de livros disponíveis na base
    ---
    tags:
      - Informações dos livros

    security:
      - BearerAuth: []

    responses:
      200:
        description: Lista de livros retornada com sucesso
        schema:
          type: object
          additionalProperties:
            type: string
        example:
          1: Dom Casmurro
          2: O Senhor dos Anéis
          3: Clean Code

      401:
        description: Token não fornecido, expirado ou inválido
        schema:
          type: object
          properties:
            error:
              type: string
              example: Token não fornecido ou inválido

      422:
        description: Token malformado ou inválido
        schema:
          type: object
          properties:
            error:
              type: string
              example: Token inválido

      500:
        description: Erro interno do servidor
    """
    try:
        if df.empty:
            return jsonify({}), 200

        dict_books = df.set_index('id')['title'].to_dict()
        return jsonify(dict_books), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500

# ============================
# Padronização JWT responses
# ============================

@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify({"error": "Token não fornecido ou inválido"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"error": "Token inválido"}), 422


# ----------------------------------------------------------------------------------------------- #
# Listar todas as categorias de livros disponíveis
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/categories', methods=['GET'])
def get_categories():
    """
    Lista categorias únicas de livros
    ---
    tags:
      - Informações dos livros

    responses:
      200:
        description: Lista de categorias retornada com sucesso
        schema:
          type: object
          properties:
            categories:
              type: array
              items:
                type: string
          example:
            categories:
              - Romance
              - Fiction
              - Science

      404:
        description: Nenhuma categoria encontrada
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: Nenhuma categoria encontrada

      500:
        description: Erro interno do servidor
    """
    try:
        categories_list = df['category'].dropna().unique().tolist()

        if not categories_list:
            return jsonify({'message': 'Nenhuma categoria encontrada'}), 404

        return jsonify({'categories': categories_list}), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500


# ----------------------------------------------------------------------------------------------- #
# Retornar detalhes completos de um livro específico pelo ID
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/<int:id>', methods=['GET'])
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
        type: integer
        description: ID do livro
        example: 10

    responses:
      200:
        description: Detalhes do livro retornados com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            category:
              type: string
            price:
              type: number
              format: float
            rating:
              type: integer
            image:
              type: string
            availability:
              type: string

      404:
        description: Livro não encontrado
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: Livro não encontrado

      500:
        description: Erro interno do servidor
    """
    try:
        livro = df[df['id'] == id]

        if livro.empty:
            return jsonify({'message': 'Livro não encontrado'}), 404

        return jsonify(livro.to_dict(orient='records')[0]), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500


# ----------------------------------------------------------------------------------------------- #
# Buscar livro por título e/ou categoria
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/search', methods=['GET'])
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
        type: string
        description: Título do livro
        example: life

      - in: query
        name: category
        required: false
        type: string
        description: Categoria de livros
        example: mystery

    responses:
      200:
        description: Lista de livros encontrados
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              category:
                type: string
              price:
                type: number
                format: float
              rating:
                type: integer
              image:
                type: string
              availability:
                type: string

      400:
        description: Nenhum parâmetro de busca informado
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: Informe ao menos um parâmetro de busca

      404:
        description: Nenhum livro encontrado
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: Nenhum livro encontrado

      500:
        description: Erro interno do servidor
    """
    title = request.args.get('title')
    category = request.args.get('category')

    if not title and not category:
        return jsonify({'error': 'Informe ao menos um parâmetro de busca'}), 400

    try:
        df_query = df.copy()

        if title:
            df_query = df_query[
                df_query['title'].str.lower().str.contains(title.lower(), na=False)
            ]

        if category:
            df_query = df_query[
                df_query['category'].str.lower().str.contains(category.lower(), na=False)
            ]

        if df_query.empty:
            return jsonify({'message': 'Nenhum livro encontrado'}), 404

        return jsonify(df_query.to_dict(orient='records')), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ----------------------------------------------------------------------------------------------- #
# Estatísticas gerais da coleção
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/stats/overview', methods=['GET'])
def get_overview():
    """
    Estatísticas gerais da coleção
    ---
    tags:
      - Stats

    responses:
      200:
        description: Estatísticas gerais retornadas com sucesso
        schema:
          type: object
          properties:
            total_books:
              type: integer
              example: 999
            mean_price:
              type: number
              format: float
              example: 35.07
            ratings_distribution:
              type: object
              additionalProperties:
                type: integer
              example:
                5: 40
                4: 55
                3: 20
                2: 5
                1: 49

      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: Erro interno do servidor
    """
    try:
        dict_overview = {
            'total_books': int(df.shape[0]),
            'mean_price': round(float(df['price'].mean()), 2) if not df.empty else 0,
            'ratings_distribution': df['rating'].value_counts().to_dict()
        }

        return jsonify(dict_overview), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500


# ----------------------------------------------------------------------------------------------- #
# Estatísticas por categoria
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/stats/categories', methods=['GET'])
def get_category_stats():
    """
    Estatísticas de livros agregadas por categoria
    ---
    tags:
      - Stats

    responses:
      200:
        description: Estatísticas por categoria retornadas com sucesso
        schema:
          type: object
          additionalProperties:
            type: object
            properties:
              n_books:
                type: integer
                example: 25
              price_min:
                type: number
                format: float
                example: 12.90
              price_max:
                type: number
                format: float
                example: 89.90
              price_mean:
                type: number
                format: float
                example: 45.30
              rating_mean:
                type: number
                format: float
                example: 4.2

      404:
        description: Nenhuma categoria encontrada
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: Nenhuma categoria encontrada

      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: Erro interno do servidor
    """
    try:
        if df.empty or 'category' not in df.columns:
            return jsonify({'message': 'Nenhuma categoria encontrada'}), 404

        lista_stats_cats = (
            df.groupby('category')
            .agg(
                n_books=('title', 'count'),
                price_min=('price', 'min'),
                price_max=('price', 'max'),
                price_mean=('price', 'mean'),
                rating_mean=('rating', 'mean')
            )
            .round(2)
            .to_dict(orient='index')
        )

        if not lista_stats_cats:
            return jsonify({'message': 'Nenhuma categoria encontrada'}), 404

        return jsonify(lista_stats_cats), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500


# ----------------------------------------------------------------------------------------------- #
# Livros com maior avaliação
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/top-rated', methods=['GET'])
def get_top_rated():
    """
    Livros com maior avaliação
    ---
    tags:
      - Informações dos livros

    responses:
      200:
        description: Lista de livros com maior avaliação
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              category:
                type: string
              price:
                type: number
                format: float
              rating:
                type: number
                format: float
              availability:
                type: string
              image:
                type: string

      404:
        description: Nenhum livro encontrado
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: Nenhum livro encontrado

      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: Erro interno do servidor
    """
    try:
        if df.empty or 'rating' not in df.columns:
            return jsonify({'message': 'Nenhum livro encontrado'}), 404

        max_rating = df['rating'].max()

        books_top_rated = df[df['rating'] == max_rating].to_dict(orient='records')

        if not books_top_rated:
            return jsonify({'message': 'Nenhum livro encontrado'}), 404

        return jsonify(books_top_rated), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500


# ----------------------------------------------------------------------------------------------- #
# Filtrar livros dentro de uma faixa de preço específica
# ----------------------------------------------------------------------------------------------- #

@bp.route('/api/v1/books/price-range', methods=['GET'])
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
        type: number
        format: float
        description: Preço mínimo
        example: 10.50

      - in: query
        name: max
        required: false
        type: number
        format: float
        description: Preço máximo
        example: 30.60

    responses:
      200:
        description: Lista de livros encontrados
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              category:
                type: string
              price:
                type: number
                format: float
              rating:
                type: integer
              image:
                type: string
              availability:
                type: string

      400:
        description: Parâmetros inválidos
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: Formato de valor inválido

      404:
        description: Nenhum livro encontrado
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: Nenhum livro encontrado

      500:
        description: Erro interno do servidor
    """
    min_price = request.args.get('min')
    max_price = request.args.get('max')

    def is_float(value: str) -> bool:
        try:
            float(value.replace(',', '.'))
            return True
        except (ValueError, TypeError):
            return False

    try:
        df_query = df.copy()

        if min_price:
            if is_float(min_price):
                df_query = df_query[df_query['price'] >= float(min_price.replace(',', '.'))]
            else:
                return jsonify({'error': 'Formato de valor inválido'}), 400

        if max_price:
            if is_float(max_price):
                df_query = df_query[df_query['price'] <= float(max_price.replace(',', '.'))]
            else:
                return jsonify({'error': 'Formato de valor inválido'}), 400

        df_query = df_query.sort_values('price')

        if df_query.empty:
            return jsonify({'message': 'Nenhum livro encontrado'}), 404

        return jsonify(df_query.to_dict(orient='records')), 200

    except Exception:
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ----------------------------------------------------------------------------------------------- #
# Verificar status da API e conectividade com os dados
# ----------------------------------------------------------------------------------------------- #

def check_database(supabase):
    try:
        supabase.table("api_request_logs").select("id").limit(1).execute()
        return True
    except Exception:
        return False


@bp.route('/api/v1/health', methods=['GET'])
def get_api_health():
    """
    Verifica o status da API e de suas dependências
    ---
    tags:
      - API Health

    responses:
      200:
        description: API saudável ou parcialmente degradada
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            api:
              type: string
              example: running
            database:
              type: string
              example: ok
            data_loaded:
              type: boolean
              example: true
            rows:
              type: integer
              example: 120
            checked_at:
              type: string
              example: 2026-01-18T14:22:30-03:00
            version:
              type: string
              example: 1.0.0
            environment:
              type: string
              example: development

      503:
        description: API indisponível ou dependência crítica falhando
        schema:
          type: object
          properties:
            status:
              type: string
              example: degraded
            api:
              type: string
              example: running
            database:
              type: string
              example: error
            data_loaded:
              type: boolean
              example: false
            rows:
              type: integer
              example: 0
            checked_at:
              type: string
              example: 2026-01-18T14:22:30-03:00
            version:
              type: string
              example: 1.0.0
            environment:
              type: string
              example: development

      500:
        description: Erro interno inesperado
        schema:
          type: object
          properties:
            error:
              type: string
          example:
            error: Erro interno do servidor
    """
    try:
        tz_sp = ZoneInfo("America/Sao_Paulo")

        health_status = {
            "status": "ok",
            "api": "running",
            "database": "ok",
            "data_loaded": False,
            "rows": 0,
            "checked_at": datetime.now(tz_sp).isoformat(),
            "version": "1.0.0",
            "environment": "development"
        }

        http_status = 200

        # Dados em memória
        if df is not None and not df.empty:
            health_status["data_loaded"] = True
            health_status["rows"] = int(df.shape[0])
        else:
            health_status["status"] = "degraded"

        # Supabase
        if not check_database(supabase):
            health_status["database"] = "error"
            health_status["status"] = "degraded"
            http_status = 503

        return jsonify(health_status), http_status

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
