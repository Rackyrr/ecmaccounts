from flask import Flask
from flask_migrate import Migrate

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
    migrate = Migrate(app, db, compare_type=True)

    # Blueprint registration

    # Main blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # CsvMailActivity blueprint
    from app.activity import bp as activity_bp
    app.register_blueprint(activity_bp, url_prefix='/activity')

    # UserToKeep blueprint
    from app.userToKeep import bp as userToKeep_bp
    app.register_blueprint(userToKeep_bp, url_prefix='/keep_user')

    # AccountAction blueprint
    from app.accountAction import bp as accountAction_bp
    app.register_blueprint(accountAction_bp, url_prefix='/account')

    # AllAccounts blueprint
    from app.allAccounts import bp as allAccounts_bp
    app.register_blueprint(allAccounts_bp, url_prefix='/all_accounts')

    # LastSetPwd blueprint
    from app.lastSetPwd import bp as lastSetPwd_bp
    app.register_blueprint(lastSetPwd_bp, url_prefix='/password')

    return app

