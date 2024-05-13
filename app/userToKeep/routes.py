from datetime import datetime

from flask import render_template

from app import db
from app.userToKeep import bp
from app.models.Account import Account
from app.models.AccountStorageTime import AccountStorageTime
from app.Ldap import Ldap


@bp.route('/')
def userToKeep():
    """
    Afficher les utilisateurs à conserver dans un tableau avec les temps de conservations.
    :return: Template html
    """
    ldap = Ldap()
    accountsReadModel = []
    emailAccounts = ldap.getAllUsersBasicInfo()
    loginWithStorageTime = (db.session.query(Account.login, Account.locked, AccountStorageTime.since,
                                             AccountStorageTime.until, AccountStorageTime.reason)
                            .join(AccountStorageTime, Account.id == AccountStorageTime.account_id).all())
    login_info = {}
    for login, locked, since, until, reason in loginWithStorageTime:

        # On récupère l'email de l'utilisateur
        accountMail = emailAccounts.get(login)
        if accountMail is None:
            accountMail = 'Non renseigné'
        else:
            accountMail = accountMail['email']

        # On vérifie si l'utilisateur est déjà dans le dictionnaire
        if login in login_info:
            # Si il est déjà dans le dictionnaire, on vérifie si le until est plus récent
            if login_info[login]['Depuis'] < since:
                # Si le until est plus récent, on le met à jour
                if until < datetime.now():
                    login_info[login] = {'Login': login, 'Email': accountMail, 'Depuis': since,
                                         'Jusqu\'à': until, 'Raison': reason, 'Délai dépassé': True,
                                         'locked': locked if locked is not None else False}
                else:
                    login_info[login] = {'Login': login, 'Email': accountMail, 'Depuis': since,
                                         'Jusqu\'à': until, 'Raison': reason, 'Délai dépassé': False,
                                         'locked': locked if locked is not None else False}
        # Si l'utilisateur n'est pas dans le dictionnaire, on l'ajoute
        else:
            if until < datetime.now():
                login_info[login] = {'Login': login, 'Email': accountMail, 'Depuis': since,
                                     'Jusqu\'à': until, 'Raison': reason, 'Délai dépassé': True,
                                     'locked': locked if locked is not None else False}
            else:
                login_info[login] = {'Login': login, 'Email': accountMail, 'Depuis': since,
                                     'Jusqu\'à': until, 'Raison': reason, 'Délai dépassé': False,
                                     'locked': locked if locked is not None else False}

    accountsReadModel = list(login_info.values())

    return render_template('userToKeep.html', donnees=accountsReadModel, lookOption=True)
