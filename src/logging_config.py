import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging(app):
    tz_sp = ZoneInfo("America/Sao_Paulo")
    timestamp = datetime.now(tz_sp).strftime("%Y-%m-%d_%H-%M-%S")

    log_file = f"{LOG_DIR}/app_{timestamp}.log"

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Logger inicializado (America/Sao_Paulo)")
