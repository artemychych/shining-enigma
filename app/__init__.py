from flask import Flask
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    
    from config import Config
    app.config.from_object(Config)
   
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models 