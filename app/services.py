"""Business logic: validation, queries, dashboard maths and demo data."""
import math
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, or_

from .database import db
from .models import Transaction

CATEGORIES = {
    "expense": [
        "Food", "Transport", "Shopping", "Bills", "Entertainment",
        "Healthcare", "Education", "Travel", "Other",
    ],
    "income": ["Salary", "Freelance", "Business", "Investment", "Other"],
}
MAX_AMOUNT = Decimal("99999999.99")


class ValidationError(Exception):
    """Raised with a dict of field -> message."""

    def __init__(self, errors):
        super().__init__("Validation failed")
        self.errors = errors


def parse_date(value):
    if not isinstance(value, str):
        raise ValueError("Date must be a string in YYYY-MM-DD format")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be a valid date in YYYY-MM-DD format")


def validate_transaction(data):
    """Return cleaned values or raise ValidationError."""
    if not isinstance(data, dict):
        raise ValidationError({"body": "Request body must be a JSON object"})

    errors, clean = {}, {}

    t = data.get("type")
    if t not in CATEGORIES:
        errors["type"] = "Type must be 'income' or 'expense'"
    else:
        clean["type"] = t

    raw = data.get("amount")
    if raw is None or raw == "" or isinstance(raw, bool):
        errors["amount"] = "Amount is required"
    else:
        try:
            amount = Decimal(str(raw)).quantize(Decimal("0.01"))
            if not amount.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            errors["amount"] = "Amount must be a number"
        else:
            if amount <= 0:
                errors["amount"] = "Amount must be greater than zero"
            elif amount > MAX_AMOUNT:
                errors["amount"] = "Amount is too large"
            else:
                clean["amount"] = amount

    cat = data.get("category")
    if not cat or not isinstance(cat, str):
        errors["category"] = "Category is required"
    elif "type" in clean and cat not in CATEGORIES[clean["type"]]:
        errors["category"] = f"'{cat}' is not a valid {clean['type']} category"
    else:
        clean["category"] = cat

    desc = data.get("description", "")
    desc = "" if desc is None else desc
    if not isinstance(desc, str):
        errors["description"] = "Description must be text"
    elif len(desc.strip()) > 200:
        errors["description"] = "Description must be 200 characters or fewer"
    else:
        clean["description"] = desc.strip()

    d = data.get("date")
    if not d:
        errors["date"] = "Date is required"
    else:
        try:
            clean["date"] = parse_date(d)
        except ValueError as exc:
            errors["date"] = str(exc)

    if errors:
        raise ValidationError(errors)
    return clean


def list_transactions(args):
    q = Transaction.query
    t = args.get("type")
    if t:
        if t not in CATEGORIES:
            raise ValidationError({"type": "Type must be 'income' or 'expense'"})
        q = q.filter(Transaction.type == t)
    if args.get("category"):
        q = q.filter(Transaction.category == args["category"])
    for key, op in (("start_date", ">="), ("end_date", "<=")):
        if args.get(key):
            try:
                d = parse_date(args[key])
            except ValueError as exc:
                raise ValidationError({key: str(exc)})
            q = q.filter(Transaction.date >= d if op == ">=" else Transaction.date <= d)
    s = (args.get("search") or "").strip()
    if s:
        like = f"%{s}%"
        q = q.filter(or_(Transaction.description.ilike(like), Transaction.category.ilike(like)))
    return q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()


def create_transaction(data):
    tx = Transaction(**validate_transaction(data))
    db.session.add(tx)
    db.session.commit()
    return tx


def update_transaction(tx, data):
    for k, v in validate_transaction(data).items():
        setattr(tx, k, v)
    db.session.commit()
    return tx


def delete_transaction(tx):
    db.session.delete(tx)
    db.session.commit()


def dashboard_summary():
    def total(kind):
        v = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.type == kind).scalar()
        return round(float(v), 2)

    income, expenses = total("income"), total("expense")

    cat_rows = (
        db.session.query(Transaction.category, func.sum(Transaction.amount))
        .filter(Transaction.type == "expense")
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    monthly = defaultdict(float)
    for d, amt in db.session.query(Transaction.date, Transaction.amount).filter(
            Transaction.type == "expense"):
        monthly[d.strftime("%Y-%m")] += float(amt)

    recent = Transaction.query.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(5).all()
    return {
        "total_income": income,
        "total_expenses": expenses,
        "balance": round(income - expenses, 2),
        "transaction_count": Transaction.query.count(),
        "category_expenses": {c: round(float(a), 2) for c, a in cat_rows},
        "monthly_expenses": {k: round(monthly[k], 2) for k in sorted(monthly)},
        "recent_transactions": [t.to_dict() for t in recent],
    }


def _demo_rows():
    """Realistic transactions spread over the last ~5 months."""
    today = date.today()
    first = today.replace(day=1)
    rows = []
    for m in range(5):
        # first day of the month, m months back
        month_start = first
        for _ in range(m):
            month_start = (month_start - timedelta(days=1)).replace(day=1)

        def d(day):
            x = month_start.replace(day=day)
            return min(x, today)

        rows += [
            ("income", 52000, "Salary", "Monthly salary", d(1)),
            ("expense", 12500, "Bills", "House rent share", d(3)),
            ("expense", 1850, "Bills", "Electricity and internet", d(6)),
            ("expense", 2400 + 150 * m, "Food", "Groceries", d(8)),
            ("expense", 780 - 40 * m, "Transport", "Metro card recharge", d(10)),
            ("expense", 1250, "Entertainment", "Movie and dinner", d(15)),
            ("expense", 3200 + 300 * (m % 3), "Shopping", "Clothes and accessories", d(19)),
            ("expense", 1500, "Education", "Online course subscription", d(22)),
        ]
        if m % 2 == 0:
            rows.append(("income", 9000 + 1000 * m, "Freelance", "Website project payment", d(12)))
    return rows


def seed_demo_data(reset=False):
    if reset:
        Transaction.query.delete()
    elif Transaction.query.count() > 0:
        return 0
    rows = _demo_rows()
    for t, amt, cat, desc, dt in rows:
        db.session.add(Transaction(type=t, amount=Decimal(amt), category=cat,
                                   description=desc, date=dt))
    db.session.commit()
    return len(rows)
