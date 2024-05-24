from flask import render_template, request, session, url_for, redirect

from app.auth import bp
from app.models.User import User


@bp.route('/')
def login_form():
    next_url = request.args.get('next')
    incorrect = request.args.get('incorrect')
    return render_template('login_page.html', next=next_url, incorrect=bool(incorrect))


@bp.route('/login_local', methods=['POST'])
def login_local():
    if request.method != 'POST':
        return 'Method not allowed', 405
    username = request.form['username']
    password = request.form['password']
    next_url = request.form['next']
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password) or user.password is None or user.password == '':
        return redirect(url_for('auth.login_form', incorrect=True, next=next_url))
    else:
        session['local_auth_profile'] = username
        return redirect(next_url) if next_url is not None else redirect(url_for('main.index'))


@bp.route('/logout')
def logout():
    session.pop('local_auth_profile', None)
    return redirect(url_for('main.index'))
