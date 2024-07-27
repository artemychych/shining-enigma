from flask import render_template


def index_page():
    context = {}
    return render_template('index.html', **context)
