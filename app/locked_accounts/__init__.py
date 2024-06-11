from flask import Blueprint

bp = Blueprint('locked_accounts', __name__)

from app.locked_accounts import routes
