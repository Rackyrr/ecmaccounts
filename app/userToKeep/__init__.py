from flask import Blueprint

bp = Blueprint('userToKeep', __name__)

from app.userToKeep import routes
