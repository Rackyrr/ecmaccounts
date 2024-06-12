from app.extensions import db
from app.models.User import User


def register_commands(app):
    @app.cli.command('create_default_user')
    def create_default_user_command():
        """Crée un utilisateur par défaut s'il n'y a aucun utilisateur local."""
        with app.app_context():
            db.create_all()
            create_default_user_local()


def create_default_user_local():
    """
    Crée un utilisateur par défaut s'il n'y a aucun utilisateur local dans la base de données.
    """
    default_username = 'admin'
    default_email = 'admin@example.net'
    default_password = 'admin'

    if User.query.filter(User.password != '').first() is None:
        user = User(username=default_username, email=default_email)
        user.set_password(default_password)
        db.session.add(user)
        db.session.commit()
        print(f'Utilisateur par défaut créé : {default_username}')
