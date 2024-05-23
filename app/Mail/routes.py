from datetime import datetime

from flask import render_template, request, current_app, redirect, url_for, flash
from jinja2 import Template
from flask_mail import Message

from app.Ldap import Ldap
from app.auth.decorators import auth_required
from app.models.TemplateMail import TemplateMail
from app.Mail import bp
from app import flaskMail, db
from app.models.History import History
from app.models.Account import Account


@bp.route('/write-mail', methods=['GET', 'POST'])
@auth_required
def writing():
    """
    Route permettant d'écrire un mail mais aussi de choisir un template et les gérer
    :return: template write-mail.html
    """
    if request.method == 'POST':
        listMail = request.form['mail']
    else:
        listMail = ''
    templates = TemplateMail.query.all()
    templatesReadModel = []
    for template in templates:
        templatesReadModel.append({
            'Nom template': template.title_template,
            'Sujet': template.subject,
            'Message': template.body
        })
    return render_template('write-mail.html', donnees=templatesReadModel, mail=listMail)


@bp.route('/send-mail', methods=['POST'])
@auth_required
def send_mail():
    """
    Route pour envoyer un mail, récupère les données du formulaire et les envoies.
    Si il y a des variables jinja dans le message, elles sont remplacées par les données qui correspondent.
    :return:
    """
    listMail = request.form['mail']
    subject = request.form['subject']
    message = request.form['message']
    reason = request.form['reason']

    report = {'Mails envoyés': {'accounts': [], 'color': 'success'},
              'Comptes non existants': {'accounts': [], 'color': 'dark'}}
    # On transforme le message en template jinja pour pouvoir remplacer les variables
    messageTemplate = Template(message)
    ldap = Ldap()
    # Pour chaque mail, on envoie le mail
    for email in listMail.split(','):
        email = email.strip()
        accountLdap = ldap.getUserByMail(email)
        if accountLdap is None:
            report['Comptes non existants']['accounts'].append(email)
            continue
        # context contient les variables jinja et ce par quoi elles doivent être remplacées
        context = {
            'name': accountLdap['name'],
        }
        # On remplace les variables jinja par les données
        result = messageTemplate.render(context)
        # On créee le message avec les infos nécessaires (sujet, expéditeur, destinataire, message)
        msg = Message(subject,
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = result
        # On envoie le mail
        flaskMail.send(msg)

        # Enregistrement de l'historique (envoie de mail)
        account = Account.query.filter_by(login=accountLdap['login']).first()
        # Si le compte n'existe pas dans la bd, on le crée
        if account is None:
            newAccount = Account(
                login=accountLdap['login'],
                uid=accountLdap['uidNumber']
            )
            db.session.add(newAccount)
            db.session.commit()
            account = Account.query.filter_by(login=accountLdap['login']).first()
        # On enregistre l'action dans l'historique
        history = History(
            date_action=datetime.now(),
            account_id=account.id,
            action_id=1,
            reason=reason
        )
        db.session.add(history)
        db.session.commit()
        report['Mails envoyés']['accounts'].append(email)

    flash(report)

    return redirect(url_for('mail.writing'))
