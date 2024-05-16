from flask import Blueprint

bp = Blueprint('waiting_to_delete', __name__)

from app.waiting_to_delete import routes
