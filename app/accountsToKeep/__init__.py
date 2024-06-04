from flask import Blueprint

bp = Blueprint('accountsToKeep', __name__)

from app.accountsToKeep import routes
