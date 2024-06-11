from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from app.extensions import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(64), index=True, unique=True)
    pre_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    locked = db.Column(db.Boolean, default=False, nullable=False)
    last_connection_date = db.Column(db.DateTime, nullable=True)
    last_connection_ip = db.Column(db.String(128), nullable=True)
    last_connection_type = db.Column(db.String(64), nullable=True)
    last_connection_service = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<Account {}>'.format(self.login)

    @hybrid_property
    def all_activity_elastic_search(self):
        activities = current_app.elasticsearch.search(index='filebeat-*', query={
            "match": {
                "username": self.login
            }
        }, size=1000)
        if activities['hits']['total']['value'] == 0:
            return None
        return activities['hits']['hits']

    @hybrid_property
    def last_activity_elastic_search(self):
        activities = current_app.elasticsearch.search(index='filebeat-*', query={
            "match": {
                "username": self.login
            }
        }, size=1, sort='@timestamp:desc')
        if activities['hits']['total']['value'] == 0:
            return None
        return activities['hits']['hits'][0]
