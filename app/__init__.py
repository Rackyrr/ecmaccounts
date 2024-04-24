from flask import Flask

from app.extensions import db
from config import Config


def create_app(config_class=Config):
    """
    Créer l'application Flask et la configurer avec la classe de configuration
    :param config_class:
    :return: Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Flask extensions
    db.init_app(app)

    # Blueprint registration

    # Main blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # CsvMailActivity blueprint
    from app.csvMailActivity import bp as csvMailActivity_bp
    app.register_blueprint(csvMailActivity_bp, url_prefix='/activity')

    # UserToKeep blueprint
    from app.userToKeep import bp as userToKeep_bp
    app.register_blueprint(userToKeep_bp, url_prefix='/keep_user')

    # AccountAction blueprint
    from app.accountAction import bp as accountAction_bp
    app.register_blueprint(accountAction_bp, url_prefix='/account')

    return app

