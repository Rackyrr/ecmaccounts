from datetime import datetime, timedelta

from flask import redirect, request, url_for, abort, render_template, current_app, flash, session
from flask_mail import Message
from jinja2 import Template

from app import db
from app import flaskMail
from app.Ldap import Ldap
from app.accountAction import bp
from app.auth.decorators import auth_required
from app.models.Account import Account
from app.models.AccountStorageTime import AccountStorageTime
from app.models.History import History
from app.models.Action import Action
from app.models.TemplateMail import TemplateMail


@bp.route('/delete', methods=['POST'])
@auth_required
def delete():
    """
    Supprimer un ou plusieurs comptes utilisateurs.
    :return: redirection vers la page précédente ou index
    """
    # On récupère les données du formulaire
    loginList = request.form['deleteListLogin']
    reason = request.form['reason']
    loginList = loginList.split(',')

    # On créée une liste de mini-rapport pour chaque login
    report = {'Comptes supprimés': {'accounts': [], 'color': 'danger'},
              'Mail d\'avertissement envoyé': {'accounts': [], 'color': 'warning'},
              'Comptes enregistrés comme à garder': {'accounts': [], 'color': 'info'},
              'Délai du mail pas encore dépassé': {'accounts': [], 'color': 'success'},
              'Comptes non existants': {'accounts': [], 'color': 'dark'}}

    ldap = Ldap()
    # On réalise les actions pour chaque login
    for login in loginList:
        account = Account.query.filter_by(login=login).first()
        # Si le compte n'existe pas dans la bd, on le prend dans le ldap
        if account is None:
            accountLdap = ldap.getUserByLogin(login)
            # Si le compte n'existe pas dans le ldap, erreur 404
            if accountLdap is None:
                report['Comptes non existants']['accounts'].append(login)
            # Si il existe, on le crée dans la bd
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()

        storageTime = AccountStorageTime.query.filter_by(account_id=account.id).all()
        # On vérifie si le compte est à garder et surtout si le temps de conservation n'est pas dépassé
        isToKeep = False
        for st in storageTime:
            if (st.until is not None) and (st.until > datetime.now()):
                report['Comptes enregistrés comme à garder']['accounts'].append(account.login)
                isToKeep = True
                continue
        if isToKeep:
            continue

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
                    history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=2, reason=reason,
                                      user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                                      else session['local_auth_profile'])
                    db.session.add(history)
                    db.session.commit()
                    report['Comptes supprimés']['accounts'].append(account.login)
                else:
                    # Si non, on ne supprime pas le compte
                    report['Délai du mail pas encore dépassé']['accounts'].append(account.login)
                    continue
            else:
                # Si il y a un mail d'annulation, on envoit un mail d'avertissement
                accountLdap = ldap.getUserByLogin(login)
                template = TemplateMail.query.filter_by(title_template="avertissement-supression").first()
                msg = Message(template.subject,
                              sender=current_app.config['MAIL_USERNAME'],
                              recipients=[accountLdap['email']])
                context = {
                    'name': accountLdap['name'],
                    'login': accountLdap['login'],
                    'reason': reason
                }
                messageTemplate = Template(template.body)
                result = messageTemplate.render(context)
                msg.body = result
                flaskMail.send(msg)
                history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=6,
                                  reason="Avertissement suppression: " + reason,
                                  user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                                  else session['local_auth_profile'])
                db.session.add(history)
                account.pre_deleted = True
                db.session.commit()
                report['Mail d\'avertissement envoyé']['accounts'].append(account.login)
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
            history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=6,
                              reason="Avertissement suppression: " + reason,
                              user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                              else session['local_auth_profile'])
            db.session.add(history)
            account.pre_deleted = True
            db.session.commit()
            report['Mail d\'avertissement envoyé']['accounts'].append(account.login)

    # On envoie le mini-rapport dans un flash
    flash(report)

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/keep', methods=['POST'])
@auth_required
def keep():
    """
    Garder un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginList = request.form['keepListLogin']
    reason = request.form['reason']
    until = request.form['until']
    loginList = loginList.split(',')

    report = {'Comptes conservés': {'accounts': [], 'color': 'info'},
              'Comptes non existants': {'accounts': [], 'color': 'dark'}}
    for login in loginList:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                report['Comptes non existants']['accounts'].append(login)
                continue
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()
        history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=3,
                          reason=reason,
                          user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                          else session['local_auth_profile'])
        db.session.add(history)
        storage_time = AccountStorageTime(account_id=account.id, since=datetime.now().replace(microsecond=0),
                                          until=until, reason=reason)
        db.session.add(storage_time)
        db.session.commit()
        report['Comptes conservés']['accounts'].append(account.login)

    flash(report)

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/lock', methods=['POST'])
@auth_required
def lock():
    """
    Bloquer un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginlist = request.form['blockListLogin']
    reason = request.form['reason']
    loginlist = loginlist.split(',')

    # Variable pour le mini-rapport
    report = {'Comptes bloqués': {'accounts': [], 'color': 'info'},
              'Comptes non existants': {'accounts': [], 'color': 'dark'}}
    for login in loginlist:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                report['Comptes non existants']['accounts'].append(login)
                continue
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()
        account.locked = True
        history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=4,
                          reason=reason,
                          user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                          else session['local_auth_profile'])
        db.session.add(history)
        db.session.commit()
        # On ajoute le compte au mini-rapport
        report['Comptes bloqués']['accounts'].append(account.login)

    # On envoie le mini-rapport dans un flash
    flash(report)

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/unlock', methods=['POST'])
@auth_required
def unlock():
    """
    Débloquer un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginlist = request.form['unblockListLogin']
    reason = request.form['reason']
    loginlist = loginlist.split(',')

    # Variable pour le mini-rapport
    report = {'Comptes débloqués': {'accounts': [], 'color': 'success'},
              'Comptes non existants': {'accounts': [], 'color': 'dark'}}
    for login in loginlist:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                report['Comptes non existants']['accounts'].append(login)
                continue
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()
        account.locked = False
        history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=5,
                          reason=reason,
                          user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                          else session['local_auth_profile'])
        db.session.add(history)
        db.session.commit()
        report['Comptes débloqués']['accounts'].append(account.login)

    # On envoie le mini-rapport dans un flash
    flash(report)

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/cancel-delete', methods=['POST'])
@auth_required
def cancel_delete():
    """
    Annuler la suppression d'un compte utilisateur.
    :return: redirection vers la page précédente ou index
    """
    loginlist = request.form['cancelDeleteListLogin']
    reason = request.form['reason']
    loginlist = loginlist.split(',')

    report = {'Annulation de la suppression': {'accounts': [], 'color': 'warning'},
              'Comptes non existants': {'accounts': [], 'color': 'dark'}}
    for login in loginlist:
        account = Account.query.filter_by(login=login).first()
        if account is None:
            ldap = Ldap()
            accountLdap = ldap.getUserByLogin(login)
            if accountLdap is None:
                report['Comptes non existants']['accounts'].append(login)
                continue
            else:
                account = Account(login=accountLdap['login'], uid=accountLdap['uidNumber'])
                db.session.add(account)
                db.session.commit()
        account.pre_deleted = False
        history = History(date_action=datetime.now().replace(microsecond=0), account_id=account.id, action_id=7,
                          reason=reason,
                          user_login=session['oidc_auth_profile']['sub'] if 'oidc_auth_profile' in session
                          else session['local_auth_profile'])
        db.session.add(history)
        db.session.commit()
        report['Annulation de la suppression']['accounts'].append(account.login)

    flash(report)

    return redirect(request.referrer or url_for('main.index'))


@bp.route('<string:login>/details')
@auth_required
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
    # Traitement de l'historique des actions sur le compte
    history = History.query.filter_by(account_id=account.id).all()
    historyReadModel = []
    for h in history:
        historyReadModel.append({'Date': h.date_action,
                                 'Action': Action.query.filter_by(action_id=h.action_id).first().label,
                                 'Raison': h.reason,
                                 'Utilisateur responsable': h.user_login})

    # Traitement des données de connexion elasticsearch
    ConnectionReadModel = []
    connections = account.all_activity_elastic_search
    if connections is not None:
        for connection in connections:
            if 'cas' in connection['_source']:
                # Convertir le timestamp en datetime :
                dateConnexion = datetime.strptime(connection['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
                dateConnexion = dateConnexion.replace(microsecond=0)
                ConnectionReadModel.append({
                    'Type de connexion': 'CAS',
                    'Date': dateConnexion,
                    'Adresse IP': connection['_source']['cas']['clientIpAddress'],
                    'Service': connection['_source']['cas']['dict_data']['service']
                    if 'dict_data' in connection['_source']['cas'] else 'Non renseigné'})
            elif 'maillog' in connection['_source']:
                dateConnexion = datetime.strptime(connection['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
                dateConnexion = dateConnexion.replace(microsecond=0)
                if 'application' in connection['_source'] and connection['_source']['application'] != '':
                    application = connection['_source']['application']
                else:
                    application = 'Mail'
                ConnectionReadModel.append({
                    'Type de connexion': 'Mail',
                    'Date': dateConnexion,
                    'Adresse IP': connection['_source']['maillog']['clientip'],
                    'Service': application})

    return render_template('accountDetails.html', user=accountLdap, donnees=historyReadModel,
                           locked=account.locked, deleted=account.deleted, connections=ConnectionReadModel)
