import json

from flask import Flask

from app import views


def create_app():
    app = Flask(__name__)

    app.config.from_file('config.json', load=json.load)

    app.add_url_rule('/', view_func=views.index_page)
    app.add_url_rule('/login/', view_func=views.login, methods=['POST'])
    app.add_url_rule('/logout/', view_func=views.logout)

    return app
