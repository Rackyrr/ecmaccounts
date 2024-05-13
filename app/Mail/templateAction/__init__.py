from flask import Blueprint

bp = Blueprint('templateAction', __name__)

from app.Mail.templateAction import routes