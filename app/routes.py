from flask import Blueprint, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from . import services as svc
from .database import db
from .models import Transaction

main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")


@main_bp.route("/")
def index():
    return render_template("index.html")


def _get_or_404(tx_id):
    tx = db.session.get(Transaction, tx_id)
    if tx is None:
        return None, (jsonify(error=f"Transaction {tx_id} not found"), 404)
    return tx, None


@api_bp.route("/health")
def health():
    return jsonify(status="ok")


@api_bp.route("/transactions", methods=["GET"])
def get_transactions():
    items = svc.list_transactions(request.args)
    return jsonify([t.to_dict() for t in items])


@api_bp.route("/transactions", methods=["POST"])
def add_transaction():
    tx = svc.create_transaction(request.get_json(silent=True))
    return jsonify(tx.to_dict()), 201


@api_bp.route("/transactions/<int:tx_id>", methods=["GET"])
def get_transaction(tx_id):
    tx, err = _get_or_404(tx_id)
    return err if err else jsonify(tx.to_dict())


@api_bp.route("/transactions/<int:tx_id>", methods=["PUT"])
def edit_transaction(tx_id):
    tx, err = _get_or_404(tx_id)
    if err:
        return err
    return jsonify(svc.update_transaction(tx, request.get_json(silent=True)).to_dict())


@api_bp.route("/transactions/<int:tx_id>", methods=["DELETE"])
def remove_transaction(tx_id):
    tx, err = _get_or_404(tx_id)
    if err:
        return err
    svc.delete_transaction(tx)
    return jsonify(message=f"Transaction {tx_id} deleted")


@api_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify(svc.dashboard_summary())


@api_bp.route("/categories", methods=["GET"])
def categories():
    return jsonify(svc.CATEGORIES)


@api_bp.route("/seed", methods=["POST"])
def seed():
    reset = request.args.get("reset", "false").lower() == "true"
    added = svc.seed_demo_data(reset=reset)
    msg = f"Added {added} demo transactions" if added else "Database already has data; nothing added"
    return jsonify(message=msg, added=added), 201 if added else 200


@api_bp.errorhandler(svc.ValidationError)
def handle_validation(exc):
    return jsonify(error="Validation failed", details=exc.errors), 400


@api_bp.errorhandler(SQLAlchemyError)
def handle_db(exc):
    db.session.rollback()
    return jsonify(error="A database error occurred"), 500


@api_bp.errorhandler(404)
def api_404(_):
    return jsonify(error="Resource not found"), 404


@api_bp.errorhandler(405)
def api_405(_):
    return jsonify(error="Method not allowed"), 405
