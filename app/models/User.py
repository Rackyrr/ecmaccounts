from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<User {}>'.format(self.login)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password_given):
        return check_password_hash(self.password, password_given)
