from app.extensions import db


class History(db.Model):
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_action = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    action_id = db.Column(db.Integer, db.ForeignKey('action.action_id'))
    reason = db.Column(db.String(128))

    def __repr__(self):
        return '<History {}>'.format(self.date_action)
