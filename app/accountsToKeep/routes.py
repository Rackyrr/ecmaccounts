from datetime import datetime

from flask import render_template, url_for, request, jsonify

from app import db
from app.auth.decorators import auth_required
from app.accountsToKeep import bp
from app.models.Account import Account
from app.models.AccountStorageTime import AccountStorageTime
from app.Ldap import Ldap


@bp.route('/')
@auth_required
def accountsToKeep():
    """
    Afficher les comptes à conserver dans un tableau avec les temps de conservations.
    :return: Template html
    """
    return render_template('accountsToKeep.html',
                           urlJS=url_for('static', filename='js/datatables_account/dataTable_accounts_to_keep.js'),
                           columnNames=['Login', 'Email', 'Depuis', 'Jusqu\'à', 'Raison',
                                        'Délai dépassé', 'Locked', 'Plus de détails'])


@bp.route('/api', methods=['GET'])
@auth_required
def get_accounts_to_keep():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables.
    :return: Reponse JSON
    """
    ldap = Ldap()
    emailAccounts = ldap.getAllUsersBasicInfo()
    loginWithStorageTime = (
        db.session.query(Account.login, Account.locked, AccountStorageTime.since,
                         AccountStorageTime.until, AccountStorageTime.reason)
        .join(AccountStorageTime, Account.id == AccountStorageTime.account_id)
        .all()
    )

    login_info = {}
    for login, locked, since, until, reason in loginWithStorageTime:
        accountMail = emailAccounts.get(login, {'email': 'Non renseigné'})['email']
        if login in login_info:
            if login_info[login]['Depuis'] < since:
                login_info[login] = {
                    'Login': login, 'Email': accountMail, 'Depuis': since,
                    'Jusqu\'à': until, 'Raison': reason,
                    'Délai dépassé': until < datetime.now(),
                    'locked': locked if locked is not None else False
                }
        else:
            login_info[login] = {
                'Login': login, 'Email': accountMail, 'Depuis': since,
                'Jusqu\'à': until, 'Raison': reason,
                'Délai dépassé': until < datetime.now(),
                'locked': locked if locked is not None else False
            }

    accountsReadModel = list(login_info.values())

    # Appliquer le filtre de recherche de DataTables
    search_value = request.args.get('search[value]', '').lower()
    filtered_accounts = [account for account in accountsReadModel if
                         search_value in account['Login'].lower() or
                         search_value in account['Email'].lower() or
                         search_value in account['Raison'].lower()]

    # Filtre Login
    search_login = request.args.get('columns[0][search][value]', '')
    if search_login:
        filtered_accounts = [account for account in filtered_accounts if search_login in account['Login']]

    # Filtre Email
    search_email = request.args.get('columns[1][search][value]', '')
    if search_email:
        filtered_accounts = [account for account in filtered_accounts if search_email in account['Email']]

    # Filtre Depuis
    search_since = request.args.get('columns[2][search][value]', '')
    if search_since:
        filtered_accounts = [account for account in filtered_accounts if search_since in str(account['Depuis'])]

    # Filtre Jusqu'à
    search_until = request.args.get('columns[3][search][value]', '')
    if search_until:
        filtered_accounts = [account for account in filtered_accounts if search_until in str(account['Jusqu\'à'])]

    # Filtre Raison
    search_raison = request.args.get('columns[4][search][value]', '')
    if search_raison:
        filtered_accounts = [account for account in filtered_accounts if search_raison in account['Raison']]

    # Filtre Délai dépassé
    search_delai_depassé = request.args.get('columns[5][search][value]', '').lower()
    if search_delai_depassé:
        filtered_accounts = [account for account in filtered_accounts if search_delai_depassé in str(account['Délai dépassé']).lower()]

    # Filtre Locked
    search_locked = request.args.get('columns[6][search][value]', '').lower()
    if search_locked:
        filtered_accounts = [account for account in filtered_accounts if search_locked in str(account['locked']).lower()]

    # Tri
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    columns = ['Login', 'Email', 'Depuis', 'Jusqu\'à', 'Raison', 'Délai dépassé', 'locked']
    sorted_accounts = sorted(filtered_accounts, key=lambda x: x[columns[order_column]], reverse=order_dir == 'desc')

    # Pagination
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    paginated_accounts = sorted_accounts[start:start + length]

    response = {
        'draw': int(request.args.get('draw', 1)),
        'recordsTotal': len(accountsReadModel),
        'recordsFiltered': len(filtered_accounts),
        'data': paginated_accounts
    }
    return jsonify(response)


