from flask import Blueprint

bp = Blueprint('lastSetPwd', __name__)

from app.lastSetPwd import routes