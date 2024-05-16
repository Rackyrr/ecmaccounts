from datetime import datetime, timedelta

from flask import redirect, request, url_for, abort, render_template, current_app
from flask_mail import Message
from jinja2 import Template

from app import db
from app import flaskMail
from app.Ldap import Ldap
from app.accountAction import bp
from app.models.Account import Account
from app.models.AccountStorageTime import AccountStorageTime
from app.models.History import History
from app.models.Action import Action
from app.models.TemplateMail import TemplateMail


@bp.route('/delete', methods=['POST'])
def delete():
    """
    Supprimer un ou plusieurs comptes utilisateurs.
    :return: redirection vers la page précédente ou index
    """
    # On récupère les données du formulaire
    loginList = request.form['deleteListLogin']
    reason = request.form['reason']
    loginList = loginList.split(',')
    ldap = Ldap()
    # On réalise les actions pour chaque login
    for login in loginList:
        account = Account.query.filter_by(login=login).first()
        # Si le compte n'existe pas dans la bd, on le prend dans le ldap
        if account is None:
            accountLdap = ldap.getUserByLogin(login)
            # Si le compte n'existe pas dans le ldap, erreur 404
            if accountLdap is None:
                return abort(404, 'Login non existant, Suppression impossible. Login : ' + login)
            # Si il existe, on le crée dans la bd
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()

        storageTime = AccountStorageTime.query.filter_by(account_id=account.id).all()
        # On vérifie si le compte est à garder et surtout si le temps de conservation n'est pas dépassé
        for st in storageTime:
            if (st.until is not None) and (st.until > datetime.now()):
                return abort(401, 'Le compte ' + login + ' ne peut pas être supprimé car il est conservé.')

        # On vérifie si un mail d'avertissement de suppression a été envoyé
        deletingMailHistory = History.query.filter_by(account_id=account.id, action_id=6).first()
        if deletingMailHistory is not None:
            # Si oui, on vérifie si un mail d'annulation de suppression a été envoyé après l'avertissement
            cancelMailHistory = History.query.filter(
                History.account_id == account.id,
                History.action_id == 7,
                History.date_action > deletingMailHistory.date_action
            ).first()
            if cancelMailHistory is None:
                # Si il n'y a pas de mail d'annulation,
                # on vérifie si l'avertissement a été envoyé il y a plus de 60 jours
                if datetime.now() - deletingMailHistory.date_action >= timedelta(days=60):
                    # Si oui, on supprime le compte
                    account.deleted = True
                    history = History(date_action=datetime.now(), account_id=account.id, action_id=2, reason=reason)
                    db.session.add(history)
                    db.session.commit()
                else:
                    # Si non, on ne supprime pas le compte
                    continue
            else:
                # Si il y a un mail d'annulation, on ne supprime pas le compte
                continue
        else:
            # Si il n'y a pas de mail d'avertissement, on envoie un mail d'avertissement
            accountLdap = ldap.getUserByLogin(login)
            # On créee le message avec les infos nécessaires (sujet, expéditeur, destinataire, message)
            template = TemplateMail.query.filter_by(title_template="avertissement-supression").first()
            msg = Message(template.subject,
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[accountLdap['email']])
            # On remplace les variables jinja par les données
            context = {
                'name': accountLdap['name'],
                'login': accountLdap['login'],
                'reason': reason
            }
            messageTemplate = Template(template.body)
            result = messageTemplate.render(context)
            msg.body = result
            # On envoie le mail
            flaskMail.send(msg)
            # On enregistre l'action dans l'historique
            history = History(date_action=datetime.now(), account_id=account.id, action_id=6,
                              reason="Avertissement suppression: " + reason)
            db.session.add(history)
            account.pre_deleted = True
            db.session.commit()

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/keep', methods=['POST'])
def keep():
    """
    Garder un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginList = request.form['keepListLogin']
    reason = request.form['reason']
    until = request.form['until']
    loginList = loginList.split(',')
    for login in loginList:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                return abort(404, 'Login non existant, Conservation impossible. Login : ' + login)
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()
        history = History(date_action=datetime.now(), account_id=account.id, action_id=3, reason=reason)
        db.session.add(history)
        storage_time = AccountStorageTime(account_id=account.id, since=datetime.now(), until=until, reason=reason)
        db.session.add(storage_time)
        db.session.commit()

        return redirect(request.referrer or url_for('main.index'))


@bp.route('/lock', methods=['POST'])
def lock():
    """
    Bloquer un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginlist = request.form['blockListLogin']
    reason = request.form['reason']
    loginlist = loginlist.split(',')
    for login in loginlist:
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
    loginlist = request.form['unblockListLogin']
    reason = request.form['reason']
    loginlist = loginlist.split(',')
    for login in loginlist:
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


@bp.route('/cancel-delete', methods=['POST'])
def cancel_delete():
    """
    Annuler la suppression d'un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginlist = request.form['cancelDeleteListLogin']
    reason = request.form['reason']
    loginlist = loginlist.split(',')
    for login in loginlist:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                return abort(404, 'Login non existant, Annulation suppression impossible. Login : ' + login)
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()
        account.pre_deleted = False
        history = History(date_action=datetime.now(), account_id=account.id, action_id=7, reason=reason)
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
