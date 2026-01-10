# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import Flask, current_app, request
import os

from src.scraping.books_ingestion import populate_books
from src.api import api_endpoints, home_layout, login_routes
from src.instances import bp, swagger, jwt
from src.logging_config import setup_logging

from vars import BASE_DIR, url_books

# ----------------------------------------------------------------------------------------------- #
# Inicializações
# ----------------------------------------------------------------------------------------------- #

# iniciar aplicação
app = Flask(__name__,
            template_folder = os.path.join(BASE_DIR, "src", "templates"),
            static_folder = os.path.join(BASE_DIR, "src", "static"))

app.config.from_object('config.Config')

# inicializar as instâncias no app
swagger.init_app(app)
jwt.init_app(app)
setup_logging(app)

# configuração de logs
@app.before_request
def log_request():
    current_app.logger.info(f"{request.method} {request.path}")

# registrar as rotas
app.register_blueprint(bp)

# ----------------------------------------------------------------------------------------------- #
# Executar o app localmente
# ----------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    with app.app_context():
        app.run(debug = True)
    