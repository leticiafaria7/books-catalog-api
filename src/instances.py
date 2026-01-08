# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask import Blueprint

# ----------------------------------------------------------------------------------------------- #
# Inicializar instâncias
# ----------------------------------------------------------------------------------------------- #

db = SQLAlchemy()
jwt = JWTManager()
swagger = Swagger()
bp = Blueprint('main', __name__)

# ----------------------------------------------------------------------------------------------- #
# Banco de usuários
# ----------------------------------------------------------------------------------------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)

# ----------------------------------------------------------------------------------------------- #
# Banco de livros
# ----------------------------------------------------------------------------------------------- #

class Book(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.Text, unique = True, nullable = False)
    price = db.Column(db.Float, nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    availability = db.Column(db.String(20), nullable = False)
    category = db.Column(db.String(20), nullable = False)
    image = db.Column(db.Text, nullable = False)

    __table_args__ = (
        db.UniqueConstraint('title', 'category', name = 'uq_book_title_category'),
    )