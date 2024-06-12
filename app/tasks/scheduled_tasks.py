from datetime import datetime

from app.extensions import db
from app.Ldap import Ldap
from app.models.Account import Account


def sync_accounts(app):
    """
    Sync accounts from LDAP to the database every 15 minutes
    """
    with app.app_context():
        app.logger.info("Synchronizing accounts")
        ldap = Ldap()

        allAccounts = ldap.getAllUsersBasicInfo()

        for login, account in allAccounts.items():
            if Account.query.filter_by(login=login).first() is None:
                new_account = Account(login=login)
                db.session.add(new_account)
                db.session.commit()
                app.logger.info(f"Account {login} created in the database")
        app.logger.info("Syncronization done")


def last_connection(app):
    """
    Update last connection for each account every hour
    """
    with app.app_context():
        app.logger.info("Updating last connection :")
        allAccounts = Account.query.all()

        for account in allAccounts:
            user_last_connection = account.last_activity_elastic_search
            if user_last_connection:
                dateLastConnection = datetime.strptime(user_last_connection['_source']['@timestamp'],
                                                       "%Y-%m-%dT%H:%M:%S.%fZ")
                if dateLastConnection != account.last_connection_date:
                    account.last_connection_date = dateLastConnection
                    if 'cas' in user_last_connection['_source']:
                        account.last_connection_type = 'CAS'
                        account.last_connection_ip = user_last_connection['_source']['cas']['clientIpAddress']
                        account.last_connection_service = user_last_connection['_source']['cas']['dict_data']['service'] \
                            if 'dict_data' in user_last_connection['_source']['cas'] else 'Non renseigné'
                    elif 'maillog' in user_last_connection['_source']:
                        account.last_connection_type = 'Mail'
                        account.last_connection_ip = user_last_connection['_source']['maillog']['clientip']
                        account.last_connection_service = 'Mail'
                    db.session.commit()
                    app.logger.info(f"Last connection updated for account {account.login}")
            else:
                if account.last_connection_date is None:
                    account.last_connection_date = datetime.min
                    account.last_connection_type = 'Pas de connexion'
                    account.last_connection_ip = 'Non renseigné'
                    account.last_connection_service = 'Non renseigné'
                    db.session.commit()
                    app.logger.info(f"Default connexion for {account.login}")
        app.logger.info("Last connection of all accounts updated")
