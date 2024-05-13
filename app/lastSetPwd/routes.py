from flask import request, current_app, render_template

from app.Ldap import Ldap
from app.lastSetPwd import bp
from app.models.Account import Account


@bp.route('/last_set', methods=['GET', 'POST'])
def last_set():
    """
    Afficher la date de dernière modification du mot de passe
    :return: Template lastSetPwd.html
    """
    if request.method == 'POST':
        days = int(request.form['password_expiration'])
    else:
        days = current_app.config['DEFAULT_PWD_LAST_SET']
    ldap = Ldap()
    accounts = ldap.getUsersWithPwdLastSetOver(days)
    accountsReadModel = []
    for account in accounts:
        account_db = Account.query.filter_by(login=account['login']).first()
        if account_db is None:
            accountsReadModel.append({
                'Login': account['login'],
                'Email': account['email'],
                'Groupe': account['groupe'],
                'Dernier changement de mot de passe': account['pwdChangedTime'],
                'Jamais modifié' : account['NeverChanged'],
                'locked': False,
            })
        else:
            accountsReadModel.append({
                'Login': account['login'],
                'Email': account['email'],
                'Groupe': account['groupe'],
                'Dernier changement de mot de passe': account['pwdChangedTime'],
                'Jamais modifié': account['NeverChanged'],
                'locked': account_db.locked,
            })

    return render_template('lastSetPwd.html', donnees=accountsReadModel, password_expiration=days,
                           lookOption=True)
