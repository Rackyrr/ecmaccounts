from flask import request, current_app, render_template, url_for, jsonify

from app.Ldap import Ldap
from app.auth.decorators import auth_required
from app.lastSetPwd import bp
from app.models.Account import Account


@bp.route('/last-set', methods=['GET', 'POST'])
@auth_required
def last_set():
    """
    Afficher la date de dernière modification du mot de passe
    :return: Template lastSetPwd.html
    """
    if request.method == 'POST':
        days = int(request.form['password_expiration'])
    else:
        days = current_app.config['DEFAULT_PWD_LAST_SET']
    return render_template('lastSetPwd.html', password_expiration=days,
                           urlJS=url_for('static', filename='js/datatables_account/dataTable_last_set_pwd.js'),
                           columnNames=['Login', 'Email', 'Groupe', 'Dernier changement de mot de passe',
                                        'Jamais modifié', 'Locked', 'Plus de détails'])


@bp.route('/api', methods=['GET'])
@auth_required
def get_last_set_pwd():
    """
    Point de terminaison API pour le traitement côté serveur de DataTables.
    :return: Reponse JSON
    """
    days = int(request.args.get('password_expiration', current_app.config['DEFAULT_PWD_LAST_SET']))
    ldap = Ldap()
    accounts = ldap.getUsersWithPwdLastSetOver(days)
    accountsReadModel = []
    for account in accounts:
        account_db = Account.query.filter_by(login=account['login']).first()
        accountsReadModel.append({
            'Login': account['login'],
            'Email': account['email'],
            'Groupe': account['groupe'],
            'Dernier changement de mot de passe': account['pwdChangedTime'],
            'Jamais modifié': account['NeverChanged'],
            'locked': account_db.locked if account_db else False,
        })

    # Appliquer le filtre de recherche de DataTables
    search_value = request.args.get('search[value]', '').lower()
    filtered_accounts = [account for account in accountsReadModel if
                         search_value in account['Login'].lower() or
                         search_value in account['Email'].lower() or
                         search_value in account['Groupe'].lower() or
                         search_value in str(account['Dernier changement de mot de passe']).lower()]

    # Filtre Login
    search_login = request.args.get('columns[0][search][value]', '')
    if search_login:
        filtered_accounts = [account for account in filtered_accounts if search_login in account['Login']]

    # Filtre Email
    search_email = request.args.get('columns[1][search][value]', '')
    if search_email:
        filtered_accounts = [account for account in filtered_accounts if search_email in account['Email']]

    # Filtre Groupe
    search_groupe = request.args.get('columns[2][search][value]', '')
    if search_groupe:
        filtered_accounts = [account for account in filtered_accounts if search_groupe in account['Groupe']]

    # Filtre Dernier changement de mot de passe
    search_pwdChangedTime = request.args.get('columns[3][search][value]', '')
    if search_pwdChangedTime:
        filtered_accounts = [account for account in filtered_accounts if
                             search_pwdChangedTime in str(account['Dernier changement de mot de passe'])]

    # Filtre Jamais modifié
    search_neverChanged = request.args.get('columns[4][search][value]', '').lower()
    if search_neverChanged:
        filtered_accounts = [account for account in filtered_accounts if
                             search_neverChanged in str(account['Jamais modifié']).lower()]

    # Filtre locked
    search_locked = request.args.get('columns[5][search][value]', '').lower()
    if search_locked:
        filtered_accounts = [account for account in filtered_accounts if
                             search_locked in str(account['locked']).lower()]

    # Tri
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    columns = ['Login', 'Email', 'Groupe', 'Dernier changement de mot de passe', 'Jamais modifié', 'locked']
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

