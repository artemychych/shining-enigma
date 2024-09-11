import json

from flask import Flask

from app import models, views


def create_app():
    app = Flask(__name__)

    app.config.from_envvar('APP_CONFIG')

    models.db.init_app(app)

    app.add_url_rule('/', view_func=views.index_page)
    app.add_url_rule('/login/', view_func=views.login, methods=['POST'])
    app.add_url_rule('/logout/', view_func=views.logout)

    app.add_url_rule('/edu_plan/', view_func=views.edu_plan_list)
    app.add_url_rule('/edu_plan_load/', view_func=views.edu_plan_load,
                     methods=['GET', 'POST'])

    return app
