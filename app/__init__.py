import secrets

from flask import Flask
from flask_migrate import Migrate

from app.extensions import db, flaskMail, oidc, scheduler, init_es
from config import Config
from app.models import TemplateMail, Account, User, Action, AccountStorageTime, History


def create_app(config_class=Config):
    """
    Créer l'application Flask et la configurer avec la classe de configuration
    :param config_class:
    :return: Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = secrets.token_hex()

    # Flask extensions
    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)
    flaskMail.init_app(app)
    oidc.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    # Elasticsearch
    app.elasticsearch = init_es(app)

    # Blueprint registration
    # Main blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # CsvMailActivity blueprint
    from app.activity import bp as activity_bp
    app.register_blueprint(activity_bp, url_prefix='/activity')

    # UserToKeep blueprint
    from app.accountsToKeep import bp as userToKeep_bp
    app.register_blueprint(userToKeep_bp, url_prefix='/keep-accounts')

    # AccountAction blueprint
    from app.accountAction import bp as accountAction_bp
    app.register_blueprint(accountAction_bp, url_prefix='/account')

    # AllAccounts blueprint
    from app.allAccounts import bp as allAccounts_bp
    app.register_blueprint(allAccounts_bp, url_prefix='/all-accounts')

    # LastSetPwd blueprint
    from app.lastSetPwd import bp as lastSetPwd_bp
    app.register_blueprint(lastSetPwd_bp, url_prefix='/password')

    # Mail blueprint
    from app.Mail import bp as mail_bp
    app.register_blueprint(mail_bp, url_prefix='/mail')

    # WaitingToDelete blueprint
    from app.waiting_to_delete import bp as waiting_to_delete_bp
    app.register_blueprint(waiting_to_delete_bp, url_prefix='/waiting-to-delete')

    # UserConnection blueprint
    from app.user_gestion import bp as user_gestion_bp
    app.register_blueprint(user_gestion_bp, url_prefix='/user_gestion')

    # Auth blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # LockedAccounts blueprint
    from app.locked_accounts import bp as locked_accounts_bp
    app.register_blueprint(locked_accounts_bp, url_prefix='/locked-accounts')

    # CLI commands
    from app.cli import init_app
    init_app(app)

    # Import tasks to register them with the scheduler
    from app import tasks

    return app
