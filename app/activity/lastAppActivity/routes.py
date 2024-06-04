from datetime import datetime
from flask import render_template, current_app, jsonify, request, url_for
from app.Ldap import Ldap
from app.activity.lastAppActivity import bp
from app.auth.decorators import auth_required
from app.models.Account import Account


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
                                        'Service', "Plus de détails"])


@bp.route('/api', methods=['GET'])
@auth_required
def get_last_activity_data():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables pour les dernières activités.
    :return: Réponse JSON
    """
    ldap = Ldap()
    accounts = ldap.getAllUsersBasicInfo()
    readModels = []
    for login, account in accounts.items():
        accountBD = Account.query.filter_by(login=login).first()
        if accountBD:
            lastActivity = accountBD.last_activity_elastic_search
        else:
            lastActivity = current_app.elasticsearch.search(index='filebeat-*', query={
                "match": {
                    "username": login
                }
            }, size=1, sort='@timestamp:desc')
            if lastActivity['hits']['total']['value'] != 0:
                lastActivity = lastActivity['hits']['hits'][0]
            else:
                lastActivity = None
        dateConnexion = datetime.min
        typelog = 'Pas de connexion'
        addressIP = 'Pas de connexion'
        service = 'Pas de connexion'
        if lastActivity is not None:
            dateConnexion = datetime.strptime(lastActivity['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            dateConnexion = dateConnexion.replace(microsecond=0)
            if 'cas' in lastActivity['_source']:
                typelog = 'CAS'
                addressIP = lastActivity['_source']['cas']['clientIpAddress']
                service = lastActivity['_source']['cas']['dict_data']['service'] \
                    if 'dict_data' in lastActivity['_source']['cas'] else 'Non renseigné'
            elif 'maillog' in lastActivity['_source']:
                typelog = 'Mail'
                addressIP = lastActivity['_source']['maillog']['clientip']
                service = 'Mail'
        readModels.append({
            'Login': login,
            'Groupe': account['groupe'],
            'Date de dernière connexion': dateConnexion,
            'Type': typelog,
            'Adresse IP': addressIP,
            'Service': service
        })

    # Appliquer les filtres de DataTables
    search_value = request.args.get('search[value]', '').lower()
    filtered_models = [account for account in readModels if
                       search_value in account['Login'].lower() or
                       search_value in account['Groupe'].lower() or
                       search_value in str(account['Date de dernière connexion']).lower() or
                       search_value in account['Type'].lower() or
                       search_value in account['Adresse IP'].lower() or
                       search_value in account['Service'].lower()]

    # Filtre Login
    search_login = request.args.get('columns[0][search][value]', '')
    if search_login:
        filtered_models = [account for account in filtered_models if search_login in account['Login']]

    # Filtre Groupe
    search_groupe = request.args.get('columns[1][search][value]', '')
    if search_groupe:
        filtered_models = [account for account in filtered_models if search_groupe in account['Groupe']]

    # Filtre Date
    search_date = request.args.get('columns[2][search][value]', '')
    if search_date:
        filtered_models = [account for account in filtered_models if search_date
                           in str(account['Date de dernière connexion'])]

    # Filtre Type
    search_type = request.args.get('columns[3][search][value]', '')
    if search_type:
        filtered_models = [account for account in filtered_models if search_type in account['Type']]

    # Filtre Adresse IP
    search_ip = request.args.get('columns[4][search][value]', '')
    if search_ip:
        filtered_models = [account for account in filtered_models if search_ip in account['Adresse IP']]

    # Filtre Service
    search_service = request.args.get('columns[5][search][value]', '')
    if search_service:
        filtered_models = [account for account in filtered_models if search_service in account['Service']]

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
