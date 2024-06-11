from flask import render_template, url_for, request, jsonify

from app.Ldap import Ldap
from app.locked_accounts import bp
from app.models.Account import Account


@bp.route('/')
def locked_accounts():
    """
    Affiche le template avec la database des comptes bloqués
    :return: Template HTML
    """
    return render_template('locked_accounts.html',
                           urlJS=url_for('static', filename='js/datatables_account/dataTable_locked_accounts.js'),
                           columnNames=['Login', 'Email', 'Groupe', 'Plus de détails'])


@bp.route('/api', methods=['GET'])
def get_locked_accounts():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables.
    :return: Réponse JSON
    """
    lockedAccounts = Account.query.filter_by(locked=True).all()
    accountsReadModel = []
    accountList = {}

    # Appliquer le filtre de recherche de DataTables
    search_value = request.args.get('search[value]', '')
    for account in lockedAccounts:
        if search_value.lower() in account.login.lower():
            accountList[account.login] = account

    # Filtre Login
    search_login = request.args.get('columns[0][search][value]', '')
    if search_login and request.args.get('columns[0][searchable]', '') == 'true':
        accountList = {login: account for login, account in accountList.items()
                       if search_login in login}

    # Get Email and Groupe
    ldap = Ldap()
    accountInfo = {}
    for login, account in accountList.items():
        accountInfo[login] = ldap.getUserByLogin(login)

    # Filtre Email
    search_email = request.args.get('columns[1][search][value]', '')
    if search_email and request.args.get('columns[1][searchable]', '') == 'true':
        accountInfo = {login: account for login, account in accountInfo.items()
                       if search_email in account['email']}

    # Filtre Groupe
    search_groupe = request.args.get('columns[2][search][value]', '')
    if search_groupe and request.args.get('columns[2][searchable]', '') == 'true':
        accountInfo = {login: account for login, account in accountInfo.items()
                       if search_groupe in account['groupe']}

    # Tri
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    if order_column == 0:
        sorted_accounts = sorted(accountInfo.items(), key=lambda x: x[0], reverse=order_dir == 'desc')
    elif order_column == 1:
        sorted_accounts = sorted(accountInfo.items(), key=lambda x: x[1]['email'], reverse=order_dir == 'desc')
    elif order_column == 2:
        sorted_accounts = sorted(accountInfo.items(), key=lambda x: x[1]['groupe'], reverse=order_dir == 'desc')
    else:
        sorted_accounts = sorted(accountInfo.items(), key=lambda x: x[0], reverse=order_dir == 'desc')

    # Pagination
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    paginated_accounts = sorted_accounts[start:start + length]

    # Construire la réponse
    for login, account in paginated_accounts:
        accountBD = Account.query.filter_by(login=login).first()
        if accountBD:
            accountsReadModel.append({'Login': login, 'Email': account['email'], 'Groupe': account['groupe']})
        else:
            accountsReadModel.append({'Login': login, 'Email': account['email'], 'Groupe': account['groupe']})

    response = {
        'draw': int(request.args.get('draw', 1)),
        'recordsTotal': len(lockedAccounts),
        'recordsFiltered': len(accountInfo),
        'data': accountsReadModel
    }
    return jsonify(response)
