from datetime import datetime, timezone

from .database import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False, index=True)  # income | expense
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(200), nullable=False, default="")
    date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "amount": float(self.amount),
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
