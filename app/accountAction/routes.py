from datetime import datetime

from flask import redirect, request, url_for, abort

from app import db
from app.Ldap import Ldap
from app.accountAction import bp
from app.models.Account import Account
from app.models.History import History
from app.models.Action import Action

# Todo : change delete route to post method


@bp.route('/delete', methods=['POST'])
def delete():
    """
    Supprimer un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginList = request.form['deleteListLogin']
    reason = request.form['reason']
    loginList = loginList.split(',')
    for login in loginList:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            userTemp = ldap.getUserByLogin(login)
            if userTemp is None:
                return abort(404, 'Login non existant, Suppression impossible. Login : ' + login)
            else:
                account = Account(login=userTemp['login'], email=userTemp['email'])
                db.session.add(account)
                db.session.commit()
        account.deleted = True
        history = History(date_action=datetime.now(), account_id=account.id, action_id=2, reason=reason)
        db.session.add(history)
        db.session.commit()

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/lock', methods=['POST'])
def lock():
    """
    Bloquer un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    login = request.form['login']
    reason = request.form['reason']
    account = Account.query.filter_by(login=login).first()
    if account is None:
        ldap = Ldap()
        userTemp = ldap.getUserByLogin(login)
        if userTemp is None:
            return abort(404, 'Login non existant, Blocage impossible. Login : ' + login)
        else:
            account = Account(login=userTemp['login'], email=userTemp['email'])
            db.session.add(account)
            db.session.commit()
    account.locked = True
    history = History(date_action=datetime.now(), account_id=account.id, action_id=4, reason=reason)
    db.session.add(history)
    db.session.commit()

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/unlock', methods=['POST'])
def unlock():
    """
    Débloquer un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    login = request.form['login']
    reason = request.form['reason']
    account = Account.query.filter_by(login=login).first()
    if account is None:
        ldap = Ldap()
        userTemp = ldap.getUserByLogin(login)
        if userTemp is None:
            return abort(404, 'Login non existant, Déblocage impossible. Login : ' + login)
        else:
            account = Account(login=userTemp['login'], email=userTemp['email'])
            db.session.add(account)
            db.session.commit()
    account.locked = False
    history = History(date_action=datetime.now(), account_id=account.id, action_id=5, reason=reason)
    db.session.add(history)
    db.session.commit()

    return redirect(request.referrer or url_for('main.index'))
