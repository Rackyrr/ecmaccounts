from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_oidc import OpenIDConnect

# Initialize extensions
db = SQLAlchemy()
flaskMail = Mail()
oidc = OpenIDConnect()


# Initialize Elasticsearch
def init_es(app):
    """
    Initialize Elasticsearch
    :param app: Flask application
    :return: Elasticsearch object instance
    """
    es_url = app.config['ELASTICSEARCH_URL']
    return Elasticsearch([es_url])
