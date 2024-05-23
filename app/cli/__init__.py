from .commands import register_commands


def init_app(app):
    """
    Initialise les commandes CLI en les enregistrant auprès de l'application Flask.
    :param app: L'application Flask
    """
    register_commands(app)
