from functools import wraps
from urllib.parse import quote_plus

from flask import session, redirect, url_for, request, abort, current_app

from app import db
from app.models.User import User


# Decorateur pour faire l'authentification avec OpenID Connect (OIDC)
def auth_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_app.config['OIDC_ENABLED'] is True:
            if session.get('oidc_auth_profile', None) is None:
                return redirect(f'{url_for("oidc_auth.login")}?next={quote_plus(request.url)}')
            else:
                user = db.session.execute(
                    db.select(User).filter_by(username=session['oidc_auth_profile']['sub'])).scalar_one_or_none()
                if user is None:
                    abort(403, 'Utilisateur non autorisé')
                try:
                    if user.email != session['oidc_auth_profile']['attributes']['email']:
                        user.email = session['oidc_auth_profile']['attributes']['email']
                        db.session.commit()
                except KeyError:
                    print('Erreur lors de la récupération de l\'adresse email')
                return view(*args, **kwargs)
        else:
            if session.get('local_auth_profile', None) is None:
                return redirect(f'{url_for("auth.login_form")}?next={quote_plus(request.url)}')
            else:
                user = User.query.filter_by(username=session['local_auth_profile']).first()
                if user is None:
                    abort(403, 'Utilisateur non autorisé')
                return view(*args, **kwargs)

    return wrapped_view
