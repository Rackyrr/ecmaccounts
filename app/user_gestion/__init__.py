from flask import Blueprint

bp = Blueprint('user_gestion', __name__)

from app.user_gestion import routes
