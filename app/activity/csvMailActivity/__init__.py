from flask import Blueprint

bp = Blueprint('csvMailActivity', __name__)

from app.activity.csvMailActivity import routes
