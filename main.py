# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import Flask, current_app, request
import os

from src.books_ingestion import populate_books
from src.api import api_endpoints, login_routes, home_layout
from src.instances import db, bp, jwt, swagger #, User, Book # não cria outras instâncias, apenas as importa: elas existem e não estão ligadas a nenhum app
from src.logging_config import setup_logging

from config import BASE_DIR #, url_books

# ----------------------------------------------------------------------------------------------- #
# Inicializações
# ----------------------------------------------------------------------------------------------- #

# iniciar aplicação
app = Flask(__name__,
            template_folder = os.path.join(BASE_DIR, "src", "templates"),
            static_folder = os.path.join(BASE_DIR, "src", "static"))

app.config.from_object('config.Config')

# inicializar as instâncias no app
db.init_app(app)
jwt.init_app(app)
swagger.init_app(app)
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

# if __name__ == '__main__':
#     with app.app_context():
#         print(BASE_DIR)
#         db.create_all()
#         print('Banco de dados criado!')
#         populate_books(url_books)
#         print('Banco de livros preenchido!')
#         app.run(debug = True)
    