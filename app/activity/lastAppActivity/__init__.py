from flask import Blueprint

bp = Blueprint('lastAppActivity', __name__)

from app.activity.lastAppActivity import routes