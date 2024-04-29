from flask import Blueprint

bp = Blueprint('allAccounts', __name__)

from app.allAccounts import routes
