# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import Flask, current_app, request

from .api import home_layout
from .extensions import db, jwt, swagger
from .logging_config import setup_logging

# ----------------------------------------------------------------------------------------------- #
# Create app
# ----------------------------------------------------------------------------------------------- #

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    setup_logging(app)

    @app.before_request
    def log_request():
        current_app.logger.info(f"{request.method} {request.path}")
    
    from .models import User, Book
    from .api import api_endpoints, login_routes
    from .extensions import bp

    app.register_blueprint(bp)
    return app