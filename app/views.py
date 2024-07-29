from functools import wraps

from flask import (abort, current_app, render_template, redirect, request,
                   session, url_for)
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def index_page():
    client_id = current_app.config['CLIENT_ID']
    return render_template('index.html', client_id=client_id)


def login():
    # Защита от CSRF
    cookie_token = request.cookies.get('g_csrf_token')
    if not cookie_token:
        return abort(400, 'No CSRF token in Cookie.')
    post_token = request.form.get('g_csrf_token')
    if not post_token:
        return abort(400, 'No CSRF token in post body.')
    if cookie_token != post_token:
        return abort(400, 'Failed to verify double submit cookie.')

    # Проверка токена
    credential = request.form.get('credential')
    if not credential:
        return abort(400, 'No ID token.')
    try:
        req = requests.Request()
        client_id = current_app.config['CLIENT_ID']
        id_info = id_token.verify_oauth2_token(credential, req, client_id)
    except GoogleAuthError:
        return abort(401, 'ID token verification error.')

    # Проверим что пользователь зарегистрирован
    email = id_info['email']
    if email not in current_app.config['USERS']:
        return abort(403, 'User is not authorized.')

    session['email'] = email
    session['username'] = id_info['name']
    session['userid'] = id_info['sub']
    next_url = request.args.get('next') or url_for('index_page')
    return redirect(next_url)


def logout():
    session.pop('email')
    session.pop('username')
    session.pop('userid')
    next_url = request.args.get('next') or url_for('index_page')
    return redirect(next_url)
