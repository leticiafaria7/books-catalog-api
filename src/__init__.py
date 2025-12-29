# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask import Flask
from .extensions import db, jwt, swagger


# ----------------------------------------------------------------------------------------------- #
# Create app
# ----------------------------------------------------------------------------------------------- #

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    
    from .models import User, Book
    from .api import api_endpoints, login_routes, pages_layout
    from .extensions import bp

    app.register_blueprint(bp)
    return app