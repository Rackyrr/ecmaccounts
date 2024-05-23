from flask import render_template

from app.auth.decorators import auth_required
from app.main import bp


@bp.route('/')
@auth_required
def index():
    return render_template('index.html')


@bp.route('/userinfo')
@auth_required
def userinfo():
    return render_template('testuserinfo.html')
