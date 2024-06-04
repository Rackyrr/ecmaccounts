from flask import Blueprint

bp = Blueprint('activity', __name__)

from app.activity.csvMailActivity import bp as csvMailActivity_bp
bp.register_blueprint(csvMailActivity_bp, url_prefix='/csv', template_folder='app/templates')

from app.activity.lastAppActivity import bp as lastAppActivity_bp
bp.register_blueprint(lastAppActivity_bp, url_prefix='/app', template_folder='app/templates')
