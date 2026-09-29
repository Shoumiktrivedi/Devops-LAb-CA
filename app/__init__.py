import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database import db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def create_app(test_config=None):
    app = Flask(__name__, instance_path=os.path.join(BASE_DIR, "instance"))
    os.makedirs(app.instance_path, exist_ok=True)

    default_db = "sqlite:///" + os.path.join(app.instance_path, "expenses.db")
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", default_db),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    from .routes import api_bp, main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(HTTPException)
    def http_error(exc):
        # JSON for API paths, default page otherwise
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify(error=exc.description), exc.code
        return exc

    with app.app_context():
        db.create_all()  # database is created automatically on startup
        if os.environ.get("SEED_ON_START", "false").lower() == "true":
            from .services import seed_demo_data
            seed_demo_data()

    return app
