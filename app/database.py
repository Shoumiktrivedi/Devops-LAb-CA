"""Database extension shared across the app (avoids circular imports)."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
