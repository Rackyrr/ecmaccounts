from app.extensions import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, index=True, unique=True)
    login = db.Column(db.String(64), index=True, unique=True)
    deleted = db.Column(db.Boolean)
    locked = db.Column(db.Boolean, default=False)
    to_keep = db.Column(db.Boolean)

    def __repr__(self):
        return '<Account {}>'.format(self.login)
