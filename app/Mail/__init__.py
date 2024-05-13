from flask import Blueprint

bp = Blueprint('mail', __name__)

from app.Mail import routes

from app.Mail.templateAction import bp as templateAction_bp
bp.register_blueprint(templateAction_bp, url_prefix='/template', template_folder='app/templates')
