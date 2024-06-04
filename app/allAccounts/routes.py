from flask import render_template, url_for, jsonify, request

from app.Ldap import Ldap
from app.allAccounts import bp
from app.auth.decorators import auth_required
from app.models.Account import Account


@bp.route('/')
@auth_required
def allAccounts():
    """
    Afficher la liste de tous les comptes utilisateurs avec la possibilité de voir les détails de chaque compte,
    en cliquant sur le bouton option.
    :return:
    """
    return render_template('allAccounts.html',
                           urlJS=url_for('static', filename='js/datatables_account/dataTable_all_accounts.js'),
                           columnNames=['Login', 'Email', 'Groupe', 'Supprimé', 'Locked', 'Plus de détails'])


@bp.route('/api', methods=['GET'])
@auth_required
def get_accounts():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables.
    :return: Réponse JSON
    """
    ldap = Ldap()
    accountsList = ldap.getAllUsersBasicInfo()
    accountsReadModel = []

    # Appliquer le filtre de recherche de DataTables
    search_value = request.args.get('search[value]', '')
    filtered_accounts = {}
    for login, account in accountsList.items():
        if (search_value.lower() in login.lower() or search_value.lower() in account['email'].lower()
                or search_value.lower() in account['groupe'].lower()):
            filtered_accounts[login] = account

    # Filtre Login
    search_login = request.args.get('columns[0][search][value]', '')
    if search_login and request.args.get('columns[0][searchable]', '') == 'true':
        filtered_accounts = {login: account for login, account in filtered_accounts.items()
                             if search_login in login}

    # Filtre Email
    search_email = request.args.get('columns[1][search][value]', '')
    if search_email and request.args.get('columns[1][searchable]', '') == 'true':
        filtered_accounts = {login: account for login, account in filtered_accounts.items()
                             if search_email in account['email']}

    # Filtre Groupe
    search_groupe = request.args.get('columns[2][search][value]', '')
    if search_groupe and request.args.get('columns[2][searchable]', '') == 'true':
        filtered_accounts = {login: account for login, account in filtered_accounts.items()
                             if search_groupe in account['groupe']}

    # Filtre Supprimé
    search_deleted = request.args.get('columns[3][search][value]', '')
    if search_deleted and request.args.get('columns[3][searchable]', '') == 'true':
        filtered_accounts = {login: account for login, account in filtered_accounts.items()
                             if search_deleted in (str(Account.query.filter_by(login=login).first().deleted).lower()
                                                   if Account.query.filter_by(login=login).first() else 'false')}

    # Filtre locked
    search_locked = request.args.get('columns[4][search][value]', '')
    if search_locked and request.args.get('columns[4][searchable]', '') == 'true':
        filtered_accounts = {login: account for login, account in filtered_accounts.items()
                             if search_locked in (str(Account.query.filter_by(login=login).first().locked).lower()
                                                  if Account.query.filter_by(login=login).first() else 'false')}

    # Tri
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    if order_column == 0:
        sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: x[0], reverse=order_dir == 'desc')
    elif order_column == 1:
        sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: x[1]['email'], reverse=order_dir == 'desc')
    elif order_column == 2:
        sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: x[1]['groupe'], reverse=order_dir == 'desc')
    elif order_column == 3:
        sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: (str(Account.query.filter_by(login=x[0])
                                                                               .first().deleted).lower()
                                                                           if Account.query.filter_by(
            login=x[0]).first() else 'false'), reverse=order_dir == 'desc')

    elif order_column == 4:
        sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: (str(Account.query.filter_by(login=x[0])
                                                                               .first().locked).lower()
                                                                           if Account.query.filter_by(
            login=x[0]).first() else 'false'), reverse=order_dir == 'desc')
    else:
        sorted_accounts = sorted(filtered_accounts.items(), key=lambda x: x[0], reverse=order_dir == 'desc')

    # Pagination
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    paginated_accounts = sorted_accounts[start:start + length]

    # Construire la réponse
    for login, account in paginated_accounts:
        accountBD = Account.query.filter_by(login=login).first()
        if accountBD:
            accountsReadModel.append({'Login': login, 'Email': account['email'], 'Groupe': account['groupe'],
                                      'Supprimé': accountBD.deleted, 'locked': accountBD.locked})
        else:
            accountsReadModel.append({'Login': login, 'Email': account['email'], 'Groupe': account['groupe'],
                                      'Supprimé': False, 'locked': False})

    response = {
        'draw': int(request.args.get('draw', 1)),
        'recordsTotal': len(accountsList),
        'recordsFiltered': len(filtered_accounts),
        'data': accountsReadModel
    }
    return jsonify(response)
