# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import logging
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask

# ----------------------------------------------------------------------------------------------- #
# Definir nome da pasta de documentação dos logs
# ----------------------------------------------------------------------------------------------- #

LOG_DIR = "logs"

# ----------------------------------------------------------------------------------------------- #
# Configurar registros de logs
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
    if not os.getenv("VERCEL"):
        tz_sp = ZoneInfo("America/Sao_Paulo")
        timestamp = datetime.now(tz_sp).strftime("%Y-%m-%d_%H-%M-%S")

        os.makedirs(LOG_DIR, exist_ok = True)
        log_file = f"{LOG_DIR}/app_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

        app.logger.info("Logger inicializado em arquivo (local)")
    else:
        app.logger.info("Logger inicializado (stdout / Vercel)")
