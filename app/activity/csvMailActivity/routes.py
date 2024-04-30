import csv
import locale
import os
from datetime import datetime, timedelta

from flask import render_template, request, current_app, redirect, url_for
from werkzeug.utils import secure_filename

from app.activity.csvMailActivity import bp
from app.models.Account import Account
from app.Ldap import Ldap

locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')


@bp.route('/upload')
def upload():
    """
    Afficher le modèle d'import CSV.
    :return: template
    """
    return render_template('uploadCSV.html')


@bp.route('/user_mail', methods=['GET', 'POST'])
def mailActivity():
    """
    Importer un fichier CSV contenant les données d'activité des utilisateurs et les traiter.
    On affiche ensuite les données traitées dans un template html.
    :return: Template rendu avec les données traitées.
    """
    if request.method == 'POST':

        if 'file' not in request.files:
            return "Aucun fichier n'a été envoyé."

        file = request.files['file']

        if file.filename == '':
            return "Aucun fichier sélectionné."

        upload_folder = current_app.config['UPLOAD_FOLDER']

        # Enregistrer le fichier téléversé dans le dossier de téléversement configuré
        file.save(os.path.join(upload_folder, secure_filename(file.filename)))

        donnees = []

        # Connection Ldap
        ldap = Ldap()
        # Lire le fichier CSV téléversé et traiter ses données
        with open(os.path.join(upload_folder, file.filename), newline='', encoding='utf-8') as csv_file:
            lecteur_csv = csv.reader(csv_file)
            infoAccounts = ldap.getAllUsersBasicInfo()
            for ligne in lecteur_csv:
                ligneTab = ligne[0].split(';')
                # Vérifier si le compte existe dans la base de données et s'il n'est pas supprimé
                # Si le compte est supprimé, passer à la ligne suivante
                account = Account.query.filter_by(login=ligneTab[1]).first()
                if (account is not None and account.deleted is False) or account is None:
                    # Calculer la date d'activité et la durée d'inactivité
                    dateActivite = datetime.strptime(ligneTab[0], "%a %d %b %Y %H:%M:%S %Z").date()
                    dureeInactif = dateActivite - timedelta(days=int(ligneTab[2]))
                    nbJourInactif = (datetime.now().date() - dureeInactif).days
                    # Déterminer l'email test de l'utilisateur à partir de LDAP
                    info = infoAccounts.get(ligneTab[1])
                    if info is not None:
                        email = info['email']
                        groupe = info['groupe']
                    else:
                        email = 'Non renseigné'
                        groupe = 'Non renseigné'
                    donnees.append({'Login': ligneTab[1], 'Email': email, "Groupe": groupe,
                                    'Dernière activité': dureeInactif, 'Nombre de jours inactif': nbJourInactif,
                                    'locked': account.locked if account is not None else False})
                else:
                    print(ligneTab[1])
                    continue

        # Rendre le modèle avec les données traitées pour affichage
        return render_template('mailActivityCSV.html', donnees=donnees,
                               filename=secure_filename(file.filename), lookOption=True)

    # Si la méthode de la requête n'est pas POST, afficher le modèle d'import CSV
    return redirect(url_for('activity.csvMailActivity.upload'))


@bp.route('/test')
def test():
    ldap = Ldap()
    return ldap.seeUserExample()
