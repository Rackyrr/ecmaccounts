from flask import Blueprint

bp = Blueprint('activity', __name__)

from app.activity.csvMailActivity import bp as csvMailActivity_bp
bp.register_blueprint(csvMailActivity_bp, url_prefix='/csv', template_folder='app/templates')
