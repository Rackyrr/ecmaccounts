from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_oidc import OpenIDConnect

db = SQLAlchemy()
flaskMail = Mail()
oidc = OpenIDConnect()


def init_es(app):
    es_url = app.config['ELASTICSEARCH_URL']
    return Elasticsearch([es_url])
