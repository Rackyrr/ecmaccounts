from flask import Blueprint

bp = Blueprint('accountAction', __name__)

from app.accountAction import routes
