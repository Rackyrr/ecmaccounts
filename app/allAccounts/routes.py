from flask import render_template

from app.Ldap import Ldap
from app.allAccounts import bp
from app.auth.decorators import auth_required
from app.models.Account import Account


@bp.route('/')
@auth_required
def allAccounts():
    """
    Afficher la liste de tous les comptes utilisateurs avec la possibilité de voir les détails de chaque compte,
    en cliquant sur le bouton option.
    :return:
    """
    ldap = Ldap()
    accountsList = ldap.getAllUsersBasicInfo()
    accountsReadModel = []
    for login, account in accountsList.items():
        accountBD = Account.query.filter_by(login=login).first()
        if accountBD :
            accountsReadModel.append({'Login': login, 'Email': account['email'], 'Groupe': account['groupe'],
                                      'Supprimé': accountBD.deleted, 'locked': accountBD.locked})
        else:
            accountsReadModel.append({'Login': login, 'Email': account['email'], 'Groupe': account['groupe'],
                                      'Supprimé': False, 'locked': False})
    return render_template('allAccounts.html', donnees=accountsReadModel, lookOption=True)
