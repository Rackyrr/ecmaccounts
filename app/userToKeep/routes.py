from flask import render_template

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
    emailAccounts = ldap.getAllUserMail()
    accounts = Account.query.filter_by(to_keep=True).all()
    for account in accounts:
        storageTime = (AccountStorageTime.query.filter_by(account_id=account.id)
                       .order_by(AccountStorageTime.since.desc()).first())
        accountMail = emailAccounts.get(account.login)
        if accountMail is None:
            accountMail = 'Non renseigné'
        accountsReadModel.append({'Login': account.login, 'Email': accountMail, 'Depuis': storageTime.since,
                                  'Jusqu\'à': storageTime.until, 'Raison': storageTime.reason})

    return render_template('userToKeep.html', accounts=accountsReadModel)
