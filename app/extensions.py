from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_oidc import OpenIDConnect

db = SQLAlchemy()
flaskMail = Mail()
oidc = OpenIDConnect()