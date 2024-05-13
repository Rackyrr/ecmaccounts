from app.extensions import db


class TemplateMail(db.Model):
    title_template = db.Column(db.String(64), primary_key=True)
    subject = db.Column(db.String(64))
    body = db.Column(db.String(250))

    def __repr__(self):
        return '<TemplateMail {}>'.format(self.subject)
