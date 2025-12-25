# app/__init__.py
import os
from flask import Flask
import importlib
from app.models import db

scheduler_started = False

def create_app():
    global scheduler_started
    app = Flask(__name__)


    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import api
    app.register_blueprint(api, url_prefix='/api/v1')

    from flasgger import Swagger
    Swagger(app)

    if not scheduler_started:
        from app.scraper import scrape_nse_kenya

        BackgroundScheduler = None
        try:
            BackgroundScheduler = importlib.import_module('apscheduler.schedulers.background').BackgroundScheduler
        except Exception:
            app.logger.warning("apscheduler not available; background jobs will be disabled")

        if BackgroundScheduler:
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                func=lambda: with_app_context_scrape(app, scrape_nse_kenya),
                trigger="interval",
                hours=6
            )
            scheduler.start()
            scheduler_started = True

        with app.app_context():
            try:
                scrape_nse_kenya()
            except Exception as e:
                app.logger.error("Initial scrape failed: %s", e)

    return app

def with_app_context_scrape(app, fn):
    with app.app_context():
        fn()