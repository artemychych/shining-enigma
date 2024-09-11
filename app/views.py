from functools import wraps
from os.path import join

from flask import (abort, current_app, render_template, redirect, request,
                   session, url_for)
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests


from app.models import db, EduPlan


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index_page'))
        return f(*args, **kwargs)
    return decorated_function


def index_page():
    """Главная страница"""
    client_id = current_app.config['CLIENT_ID']
    return render_template('index.html', client_id=client_id)


def login():
    """Вход пользователя в систему"""

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
    token = request.form.get('credential')
    if not token:
        return abort(400, 'No ID token.')
    req = requests.Request()
    client_id = current_app.config['CLIENT_ID']
    try:
        payload = id_token.verify_oauth2_token(token, req, client_id)
    except GoogleAuthError:
        return abort(401, 'ID token verification error.')

    # Проверим что пользователь зарегистрирован
    email = payload['email']
    if email not in current_app.config['USERS']:
        return abort(403, 'User is not authorized.')

    session['user'] = {
        'email': email,
        'id': payload['sub'],
        'name': payload['name'],
    }
    return redirect(url_for('index_page'))


def logout():
    """Выход пользователя из системы"""
    session.pop('user')
    return redirect(url_for('index_page'))


@login_required
def edu_plan_list():
    """Список учебных планов"""
    query = db.select(EduPlan).order_by(EduPlan.code)
    edu_plans = db.session.execute(query).scalars()
    return render_template('edu_plan_list.html', edu_plans=edu_plans)


@login_required
def edu_plan_load():
    """Загрузка учебного плана"""
    if request.method == 'POST':
        plan = request.files['plan']
        EduPlan.load(plan.filename, plan.stream.read())
        return redirect(url_for('edu_plan_list'))
    return render_template('edu_plan_load.html')
