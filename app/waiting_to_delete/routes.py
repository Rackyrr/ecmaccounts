from flask import render_template, request, url_for, jsonify

from app.Ldap import Ldap
from app.auth.decorators import auth_required
from app.models.Account import Account
from app.models.History import History
from app.models.Action import Action
from app.waiting_to_delete import bp

from app import db


@bp.route('/accounts-waiting-to_delete')
@auth_required
def user_waiting_to_delete():
    """
    Route permettant d'afficher les utilisateurs en attente de suppression
    :return: template user-waiting-to_delete.html
    """
    return render_template('pre_deleted_accounts.html',
                           urlJS=url_for('static', filename='js/datatables_account/dataTable_waiting_to_delete.js'),
                           columnNames=['Login', 'Email', 'Raison', 'Date de l\'avertissement', 'locked',
                                        'Plus de détails'])


@bp.route('/api', methods=['GET'])
@auth_required
def get_users_waiting_to_delete():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables pour les utilisateurs en
    attente de suppression.
    """
    # Requête pour récupérer les utilisateurs en attente de suppression
    query = (
        db.session.query(
            Account.login,
            History.date_action,
            History.reason,
        )
        .join(History, Account.id == History.account_id)
        .join(Action, History.action_id == Action.action_id)
        .filter(History.action_id == 6)
        .filter(Account.pre_deleted)
        .filter(Account.deleted == False)
    )
    results = db.session.execute(query).fetchall()
    ldap = Ldap()
    accountsList = []

    for account in results:
        account_ldap = ldap.getUserByLogin(account.login)
        accountDB = Account.query.filter_by(login=account.login).first()

        accountsList.append({
            "Login": account.login,
            "Email": account_ldap['email'] if account_ldap is not None else 'Non renseigné',
            "Raison": account.reason,
            "Date de l'avertissement": account.date_action,
            'locked': accountDB.locked if accountDB is not None else False
        })

    # Appliquer le filtre de recherche de DataTables
    search_value = request.args.get('search[value]', '').lower()
    filtered_accounts = [account for account in accountsList if
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

    # Filtre Raison
    search_raison = request.args.get('columns[2][search][value]', '')
    if search_raison:
        filtered_accounts = [account for account in filtered_accounts if search_raison in account['Raison']]

    # Filtre Date de l'avertissement
    search_date = request.args.get('columns[3][search][value]', '')
    if search_date:
        filtered_accounts = [account for account in filtered_accounts if search_date
                             in str(account['Date de l\'avertissement'])]

    # Filtre locked
    search_locked = request.args.get('columns[4][search][value]', '').lower()
    if search_locked:
        filtered_accounts = [account for account in filtered_accounts if search_locked in str(account['locked']).lower()]

    # Tri
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    columns = ['Login', 'Email', 'Raison', 'Date de l\'avertissement', 'locked']
    sorted_accounts = sorted(filtered_accounts, key=lambda x: x[columns[order_column]], reverse=order_dir == 'desc')

    # Pagination
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    paginated_accounts = sorted_accounts[start:start + length]

    response = {
        'draw': int(request.args.get('draw', 1)),
        'recordsTotal': len(accountsList),
        'recordsFiltered': len(filtered_accounts),
        'data': paginated_accounts
    }
    return jsonify(response)

