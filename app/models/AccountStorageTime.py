from app.extensions import db


class AccountStorageTime(db.Model):
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    since = db.Column(db.DateTime, primary_key=True)
    until = db.Column(db.DateTime)
    reason = db.Column(db.String(128))

    def __repr__(self):
        return '<accountStorageTime {}>'.format(self.since)
