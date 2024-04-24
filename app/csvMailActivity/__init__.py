from flask import Blueprint

bp = Blueprint('csvMailActivity', __name__)

from app.csvMailActivity import routes
