import pytest

from app import create_app
from app.database import db


@pytest.fixture()
def client(tmp_path):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
    })
    with app.app_context():
        yield app.test_client()
        db.session.remove()
        db.drop_all()


VALID = {"type": "expense", "amount": 250.5, "category": "Food",
         "description": "Lunch", "date": "2025-01-15"}


def make(client, **over):
    return client.post("/api/transactions", json={**VALID, **over})


def test_app_starts_and_serves_ui(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Personal Expense Tracker" in r.data
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_get_transactions_empty(client):
    r = client.get("/api/transactions")
    assert r.status_code == 200 and r.get_json() == []


def test_create_transaction(client):
    r = make(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body["id"] == 1 and body["amount"] == 250.5 and body["category"] == "Food"
    assert len(client.get("/api/transactions").get_json()) == 1


def test_get_transaction_by_id(client):
    tx_id = make(client).get_json()["id"]
    r = client.get(f"/api/transactions/{tx_id}")
    assert r.status_code == 200 and r.get_json()["description"] == "Lunch"
    assert client.get("/api/transactions/999").status_code == 404


def test_update_transaction(client):
    tx_id = make(client).get_json()["id"]
    r = client.put(f"/api/transactions/{tx_id}",
                   json={**VALID, "amount": 300, "category": "Travel"})
    assert r.status_code == 200
    assert r.get_json()["amount"] == 300 and r.get_json()["category"] == "Travel"
    assert client.put("/api/transactions/999", json=VALID).status_code == 404


def test_delete_transaction(client):
    tx_id = make(client).get_json()["id"]
    assert client.delete(f"/api/transactions/{tx_id}").status_code == 200
    assert client.get(f"/api/transactions/{tx_id}").status_code == 404
    assert client.delete(f"/api/transactions/{tx_id}").status_code == 404


@pytest.mark.parametrize("override", [
    {"amount": -5},
    {"amount": 0},
    {"amount": "abc"},
    {"amount": None},
    {"type": "gift"},
    {"category": ""},
    {"category": "Salary"},          # income category on an expense
    {"date": "2025-13-45"},
    {"date": ""},
])
def test_invalid_transaction_rejected(client, override):
    r = make(client, **override)
    assert r.status_code == 400
    assert "details" in r.get_json()
    assert client.get("/api/transactions").get_json() == []


def test_missing_or_bad_body(client):
    assert client.post("/api/transactions", data="not json").status_code == 400


def test_filters_and_search(client):
    make(client)
    make(client, type="income", category="Salary", amount=1000,
         description="Pay", date="2025-02-01")
    make(client, category="Transport", description="Bus", date="2025-03-01")
    get = lambda q: client.get("/api/transactions" + q).get_json()
    assert len(get("?type=income")) == 1
    assert len(get("?category=Transport")) == 1
    assert len(get("?start_date=2025-02-01&end_date=2025-02-28")) == 1
    assert len(get("?search=lunch")) == 1
    assert len(get("?search=sal")) == 1          # matches category
    assert client.get("/api/transactions?start_date=bad").status_code == 400


def test_dashboard(client):
    make(client, amount=100, category="Food", date="2025-01-10")
    make(client, amount=50, category="Travel", date="2025-02-10")
    make(client, type="income", category="Salary", amount=1000, date="2025-01-01")
    d = client.get("/api/dashboard").get_json()
    assert d["total_income"] == 1000
    assert d["total_expenses"] == 150
    assert d["balance"] == 850
    assert d["transaction_count"] == 3
    assert d["category_expenses"] == {"Food": 100, "Travel": 50}
    assert d["monthly_expenses"] == {"2025-01": 100, "2025-02": 50}
    assert len(d["recent_transactions"]) == 3


def test_categories(client):
    r = client.get("/api/categories")
    data = r.get_json()
    assert r.status_code == 200
    assert "Food" in data["expense"] and "Salary" in data["income"]


def test_seed(client):
    r = client.post("/api/seed")
    assert r.status_code == 201 and r.get_json()["added"] > 0
    assert client.post("/api/seed").get_json()["added"] == 0     # idempotent
    assert client.post("/api/seed?reset=true").status_code == 201
    assert client.get("/api/dashboard").get_json()["transaction_count"] > 0


def test_unknown_api_route_is_json(client):
    r = client.get("/api/nope")
    assert r.status_code == 404 and "error" in r.get_json()
