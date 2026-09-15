import os
import secrets
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from . import models  # noqa: F401

    with app.app_context():
    db.create_all()

    from .auth import auth_bp
    from .routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.before_request
    def issue_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)

    @app.context_processor
    def inject_globals():
        return {"csrf_token": session.get("csrf_token", "")}

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database initialized.")

    @app.errorhandler(404)
    def missing_page(error):
        from flask import render_template
        return render_template("error.html", code=404, message="This screen does not exist."), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        from flask import render_template
        return render_template("error.html", code=500, message="The arcade is temporarily unavailable."), 500

    return app
