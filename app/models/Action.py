from app.extensions import db


class Action(db.Model):
    action_id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(128))

    def __repr__(self):
        return '<Action {}>'.format(self.label)
