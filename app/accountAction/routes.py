from datetime import datetime

from flask import redirect, request, url_for, abort, render_template

from app import db
from app.Ldap import Ldap
from app.accountAction import bp
from app.models.Account import Account
from app.models.History import History
from app.models.Action import Action


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
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                return abort(404, 'Login non existant, Suppression impossible. Login : ' + login)
            else:
                account = Account(login=accountLdap['login'], email=accountLdap['email'])
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
        accountLdap = ldap.getUserByLogin(login)
        if accountLdap is None:
            return abort(404, 'Login non existant, Blocage impossible. Login : ' + login)
        else:
            account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
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
        accountLdap = ldap.getUserByLogin(login)
        if accountLdap is None:
            return abort(404, 'Login non existant, Déblocage impossible. Login : ' + login)
        else:
            account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
            db.session.add(account)
            db.session.commit()
    account.locked = False
    history = History(date_action=datetime.now(), account_id=account.id, action_id=5, reason=reason)
    db.session.add(history)
    db.session.commit()

    return redirect(request.referrer or url_for('main.index'))


@bp.route('<string:login>/details')
def details(login):
    """
    Afficher les détails d'un compte utilisateur.
    :param login: login de l'utilisateur
    :return: Template html
    """
    account = Account.query.filter_by(login=login).first()
    ldap = Ldap()
    accountLdap = ldap.getUserByLogin(login)
    if account is None:
        if accountLdap is None:
            return abort(404, 'Login non existant, Détails impossible. Login : ' + login)
        else:
            account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
            db.session.add(account)
            db.session.commit()
    history = History.query.filter_by(account_id=account.id).all()
    historyReadModel = []
    for h in history:
        historyReadModel.append({'Date': h.date_action,
                                 'Action': Action.query.filter_by(action_id=h.action_id).first().label,
                                 'Raison': h.reason})
    return render_template('accountDetails.html', user=accountLdap, donnees=historyReadModel,
                           locked=account.locked, deleted=account.deleted)
