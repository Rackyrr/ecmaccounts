from flask import render_template, current_app, redirect, request, url_for, flash

from app import db
from app.auth.decorators import auth_required
from app.user_gestion import bp
from app.models.User import User


@bp.route('/')
@auth_required
def user_gestion():
    userList = User.query.all()
    usersReadModel = []
    for user in userList:
        usersReadModel.append({'username': user.username, 'mail': user.email})
    return render_template('new_user_form.html', donnees=usersReadModel,
                           oidc_enabled=current_app.config['OIDC_ENABLED'])


@bp.route('/add_user', methods=['POST'])
@auth_required
def add_user():
    if request.method != 'POST':
        return 'Method not allowed', 405
    username = request.form['username']
    email = request.form['mail']
    if not current_app.config['OIDC_ENABLED']:
        password = request.form['password']
    else:
        password = None
    user = User(username=username, email=email)
    if not current_app.config['OIDC_ENABLED']:
        user.set_password(password) if password else None
    db.session.add(user)
    db.session.commit()

    flash({'Création d\'un compte utilisateur': {'accounts': [username], 'color': 'success'}})

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/delete_user/<string:username>')
@auth_required
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return 'User not found', 404
    db.session.delete(user)
    db.session.commit()

    flash({'Suppression d\'un compte utilisateur': {'accounts': [username], 'color': 'danger'}})

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/edit_user/<string:username>', methods=['POST'])
@auth_required
def edit_user(username):
    if request.method != 'POST':
        return 'Method not allowed', 405
    user = User.query.filter_by(username=username).first()
    if user is None:
        return 'User not found', 404
    user.email = request.form['mail'] if request.form['mail'] else user.email
    password = request.form['password']
    if password is not None and password != '':
        password_confirm = request.form['confirmPassword']
        if password != password_confirm or password_confirm == '' or password_confirm is None:
            return 'Passwords do not match', 400
        user.set_password(password)
    db.session.commit()

    flash({'Modification d\'un compte utilisateur': {'accounts': [username], 'color': 'info'}})

    return redirect(request.referrer or url_for('main.index'))
