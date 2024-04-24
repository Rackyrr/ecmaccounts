from datetime import datetime

from flask import redirect, request, url_for

from app import db
from app.Ldap import Ldap
from app.accountAction import bp
from app.models.Account import Account
from app.models.History import History
from app.models.Action import Action


@bp.route('<string:login>/delete')
def delete(login):
    """
    Supprimer un compte utilisateur.
    :param login: login de l'utilisateur
    :return: redirection vers la page précédente ou index
    """
    account = Account.query.filter_by(login=login).first()
    if account is None:
        ldap = Ldap()
        userTemp = ldap.getUserByLogin(login)
        account = Account(login=userTemp['login'], email=userTemp['email'])
        db.session.add(account)
        db.session.commit()

    account.deleted = True
    history = History(date_action=datetime.now(), account_id=account.id, action_id=2, reason='')
    db.session.add(history)
    db.session.commit()

    return redirect(request.referrer or url_for('main.index'))


@bp.route('<string:login>/lock')
def lock(login):
    """
    Bloquer un compte utilisateur.
    :param login: login de l'utilisateur
    :return: redirection vers la page précédente ou index
    """
    account = Account.query.filter_by(login=login).first()
    if account is None:
        ldap = Ldap()
        userTemp = ldap.getUserByLogin(login)
        account = Account(login=userTemp['login'], email=userTemp['email'])
        db.session.add(account)
        db.session.commit()
    account.locked = True
    history = History(date_action=datetime.now(), account_id=account.id, action_id=4, reason='')
    db.session.add(history)
    db.session.commit()

    return redirect(request.referrer or url_for('main.index'))


@bp.route('<string:login>/unlock')
def unlock(login):
    """
    Débloquer un compte utilisateur.
    :param login: login de l'utilisateur
    :return: redirection vers la page précédente ou index
    """
    account = Account.query.filter_by(login=login).first()
    if account is None:
        ldap = Ldap()
        userTemp = ldap.getUserByLogin(login)
        account = Account(login=userTemp['login'], email=userTemp['email'])
        db.session.add(account)
        db.session.commit()
    account.locked = False
    history = History(date_action=datetime.now(), account_id=account.id, action_id=5, reason='')
    db.session.add(history)
    db.session.commit()

    return redirect(request.referrer or url_for('main.index'))
