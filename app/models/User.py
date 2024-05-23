import bcrypt

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<User {}>'.format(self.login)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password_given):
        return bcrypt.checkpw(password_given.encode('utf-8'), self.password.encode('utf-8'))
