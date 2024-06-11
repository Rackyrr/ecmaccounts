from datetime import datetime
from flask import render_template, current_app, jsonify, request, url_for
from app.Ldap import Ldap
from app.activity.lastAppActivity import bp
from app.auth.decorators import auth_required
from app.models.Account import Account
from sqlalchemy import or_


@bp.route('/last_activity')
@auth_required
def last_activity():
    """
    Afficher tous les utilisateurs et leur dernière connexion (Mail ou CAS).
    :return: template
    """
    return render_template('last_connexion.html',
                           urlJS=url_for('static',
                                         filename='js/datatables_account/dataTable_accounts_last_app_activity.js'),
                           columnNames=['Login', 'Groupe', 'Date de dernière connexion', 'Type', 'Adresse IP',
                                        'Service', 'Plus de détails'])


@bp.route('/api', methods=['GET'])
@auth_required
def get_last_activity_data():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables pour les dernières activités.
    :return: Réponse JSON
    """
    ldap = Ldap()
    accounts = ldap.getAllUsersBasicInfo()

    # Collecter les logins des utilisateurs LDAP
    logins = accounts.keys()

    # Récupérer tous les comptes en une seule requête
    accountsBD = Account.query.filter(Account.login.in_(logins)).all()

    readModels = []
    for accountBD in accountsBD:
        login = accountBD.login
        account = accounts[login]
        readModels.append({
            'Login': login,
            'Groupe': account['groupe'],
            'Date de dernière connexion': accountBD.last_connection_date,
            'Type': accountBD.last_connection_type,
            'Adresse IP': accountBD.last_connection_ip,
            'Service': accountBD.last_connection_service
        })

    # Appliquer les filtres de DataTables
    search_value = request.args.get('search[value]', '').lower()
    if search_value:
        filtered_models = [account for account in readModels if
                           search_value in account['Login'].lower() or
                           search_value in account['Groupe'].lower() or
                           search_value in str(account['Date de dernière connexion']).lower() or
                           search_value in account['Type'].lower() or
                           search_value in account['Adresse IP'].lower() or
                           search_value in account['Service'].lower()]
    else:
        filtered_models = readModels

    # Appliquer les filtres colonne par colonne
    filters = {
        'Login': request.args.get('columns[0][search][value]', ''),
        'Groupe': request.args.get('columns[1][search][value]', ''),
        'Date de dernière connexion': request.args.get('columns[2][search][value]', ''),
        'Type': request.args.get('columns[3][search][value]', ''),
        'Adresse IP': request.args.get('columns[4][search][value]', ''),
        'Service': request.args.get('columns[5][search][value]', '')
    }

    for key, search in filters.items():
        if search:
            filtered_models = [account for account in filtered_models if search.lower() in str(account[key]).lower()]

    # Tri
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    columns = ['Login', 'Groupe', 'Date de dernière connexion', 'Type', 'Adresse IP', 'Service']
    sorted_models = sorted(filtered_models, key=lambda x: x[columns[order_column]], reverse=order_dir == 'desc')

    # Pagination
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    paginated_models = sorted_models[start:start + length]

    response = {
        'draw': int(request.args.get('draw', 1)),
        'recordsTotal': len(readModels),
        'recordsFiltered': len(filtered_models),
        'data': paginated_models
    }
    return jsonify(response)
