from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), index=True, unique=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.login)
