from flask import Flask

import views


def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', endpoint='index_page', view_func=views.index_page)
    return app
