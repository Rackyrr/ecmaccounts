from app.extensions import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, index=True, unique=True)
    login = db.Column(db.String(64), index=True, unique=True)
    pre_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    locked = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Account {}>'.format(self.login)
