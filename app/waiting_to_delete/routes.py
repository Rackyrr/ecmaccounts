from flask import render_template

from app.Ldap import Ldap
from app.auth.decorators import auth_required
from app.models.Account import Account
from app.models.History import History
from app.models.Action import Action
from app.waiting_to_delete import bp

from app import db


@bp.route('/user-waiting-to_delete')
@auth_required
def user_waiting_to_delete():
    """
    Route permettant d'afficher les utilisateurs en attente de suppression
    :return: template user-waiting-to_delete.html
    """
    query = (
        db.session.query(
            Account.login,
            History.date_action,
            History.reason,
        )
        .join(History, Account.id == History.account_id)
        .join(Action, History.action_id == Action.action_id)
        .filter(History.action_id == 6)
        .filter(Account.pre_deleted)
        .filter(Account.deleted == False)
    )
    results = db.session.execute(query).fetchall()
    ldap = Ldap()
    accountsReadModel = []

    for account in results:
        account_ldap = ldap.getUserByLogin(account.login)
        accountDB = Account.query.filter_by(login=account.login).first()
        accountsReadModel.append({
            "Login": account.login,
            "Email": account_ldap['email'],
            "Raison": account.reason,
            "Date de l\'avertissement": account.date_action,
            'locked': accountDB.locked if accountDB is not None else False})

    return render_template('pre_deleted_accounts.html', donnees=accountsReadModel, lookOption=True)
