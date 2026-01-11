# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import logging
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, g, current_app
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

# ----------------------------------------------------------------------------------------------- #
# Definir nome da pasta de documentação dos logs
# ----------------------------------------------------------------------------------------------- #

LOG_DIR = "logs"

# ----------------------------------------------------------------------------------------------- #
# Configurar registros de logs (local e flask)
# ----------------------------------------------------------------------------------------------- #

def setup_logging(app: Flask) -> None:
    """
    Configura o sistema de logging da aplicação com fuso horário local.

    Esta função define um manipulador de arquivos (FileHandler) para capturar logs
    da aplicação, formatando-os com data/hora de São Paulo e salvando-os em um
    diretório específico definido pela constante LOG_DIR.

    Args:
        app (Flask): A instância da aplicação Flask que receberá a configuração de log.

    Returns:
        None: A função altera o estado do objeto app e não retorna valores.

    Raises:
        OSError: Pode ocorrer se o diretório LOG_DIR não existir ou não for gravável.
    """

    # definir o layout da mensagem: [Data/Hora] Nível de Severidade em NomeDoModulo: Mensagem
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # limpar handlers existentes
    app.logger.handlers.clear()
    app.logger.setLevel(logging.INFO)

    # sempre logar em stdout (Vercel captura)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(stream_handler)

    # SOMENTE LOCAL: criar pasta e arquivo
    if os.getenv("FLASK_ENV") == "development":
        tz_sp = ZoneInfo("America/Sao_Paulo")
        timestamp = datetime.now(tz_sp).strftime("%Y-%m-%d_%H-%M-%S")

        os.makedirs(LOG_DIR, exist_ok = True)
        log_file = f"{LOG_DIR}/app_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

        app.logger.info("Logger inicializado em arquivo (local)")
    else:
        app.logger.info("Logger inicializado (stdout / Render)")

# ----------------------------------------------------------------------------------------------- #
# Configurar registros de logs (supabase)
# ----------------------------------------------------------------------------------------------- #

def register_request_logging(app, supabase):
    tz_sp = ZoneInfo("America/Sao_Paulo")

    IGNORED_PATHS = {
        "/flasgger_static/swagger-ui-standalone-preset.js",
        "/apispec_1.json",
        "/flasgger_static/swagger-ui.css",
        "/flasgger_static/swagger-ui-bundle.js",
        "/static/github.png",
        "/flasgger_static/lib/jquery.min.js",
        "/static/styles.css",
        "/static/question_mark.png",
    }

    # Carregar usuário (ANTES do logging e do after_request)
    @app.before_request
    def load_user():
        try:
            verify_jwt_in_request(optional=True)
            g.user_id = get_jwt_identity()
        except Exception:
            g.user_id = None

    # Log simples em stdout
    @app.before_request
    def log_request():
        g.request_start_time = datetime.now(tz_sp)
        current_app.logger.info(
            f"{request.method} {request.path}"
        )

    # Log estruturado no Supabase
    def log_request_to_supabase_factory(supabase):
        def log_request_to_supabase(response):
            if request.path in IGNORED_PATHS:
                return response

            try:
                supabase.table("api_request_logs").insert({
                    "user_id": g.user_id,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                }).execute()

            except Exception as e:
                current_app.logger.error(
                    f"Erro ao salvar log no Supabase: {e}"
                )

            return response

        return log_request_to_supabase

    app.after_request(log_request_to_supabase_factory(supabase))

    # Tratamento de exceções
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        current_app.logger.exception(e)
        return {"error": "internal server error"}, 500
