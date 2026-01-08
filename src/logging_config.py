# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask

# ----------------------------------------------------------------------------------------------- #
# Criar pasta se não existir
# ----------------------------------------------------------------------------------------------- #

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok = True)

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

    # definir o fuso horário para garantir consistência nos nomes dos arquivos
    tz_sp = ZoneInfo("America/Sao_Paulo")
    timestamp = datetime.now(tz_sp).strftime("%Y-%m-%d_%H-%M-%S")

    # definir o caminho completo do arquivo de log baseado no timestamp atual
    log_file = f"{LOG_DIR}/app_{timestamp}.log"

    # definir o layout da mensagem: [Data/Hora] Nível de Severidade em NomeDoModulo: Mensagem
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # configurar o handler para gravar as mensagens no arquivo físico
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # limpar os handlers existentes para evitar duplicidade de mensagens (ex: logs padrão do Flask)
    app.logger.handlers.clear()

    # adicionar o novo handler configurado e define o nível mínimo de captura para INFO
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # log de confirmação da inicialização bem-sucedida
    app.logger.info("Logger inicializado (America/Sao_Paulo)")
