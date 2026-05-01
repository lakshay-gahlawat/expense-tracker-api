# NEW
from datetime import datetime, timezone
TIMESTAMP = datetime.now(timezone.utc).isoformat()


def make_transaction(account_id, amount=500, t_type="expense", category="Food"):
    return {
        "account_id": account_id,
        "amount": amount,
        "transaction_type": t_type,
        "category": category,
        "date": TIMESTAMP,
    }


class TestCreateTransaction:
    def test_create_success(self, client, auth_headers, account):
        res = client.post("/transactions/", json=make_transaction(account["id"]), headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert float(data["amount"]) == 500.0
        assert data["transaction_type"] == "expense"

    def test_invalid_type(self, client, auth_headers, account):
        payload = make_transaction(account["id"])
        payload["transaction_type"] = "refund"
        res = client.post("/transactions/", json=payload, headers=auth_headers)
        assert res.status_code == 422

    def test_wrong_account(self, client, auth_headers):
        payload = make_transaction("nonexistent-account-id")
        res = client.post("/transactions/", json=payload, headers=auth_headers)
        assert res.status_code == 404


class TestGetTransactions:
    def test_list_transactions(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"]), headers=auth_headers)
        res = client.get("/transactions/", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_filter_by_type(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"], t_type="income"), headers=auth_headers)
        client.post("/transactions/", json=make_transaction(account["id"], t_type="expense"), headers=auth_headers)
        res = client.get("/transactions/?transaction_type=income", headers=auth_headers)
        for t in res.json()["items"]:
            assert t["transaction_type"] == "income"

    def test_filter_by_category(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"], category="Rent"), headers=auth_headers)
        client.post("/transactions/", json=make_transaction(account["id"], category="Food"), headers=auth_headers)
        res = client.get("/transactions/?category=Rent", headers=auth_headers)
        for t in res.json()["items"]:
            assert "Rent" in t["category"]

    def test_search(self, client, auth_headers, account):
        payload = make_transaction(account["id"])
        payload["description"] = "Monthly grocery run"
        client.post("/transactions/", json=payload, headers=auth_headers)
        res = client.get("/transactions/?search=grocery", headers=auth_headers)
        assert res.json()["total"] >= 1

    def test_amount_filter(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"], amount=100), headers=auth_headers)
        client.post("/transactions/", json=make_transaction(account["id"], amount=900), headers=auth_headers)
        res = client.get("/transactions/?min_amount=500", headers=auth_headers)
        for t in res.json()["items"]:
            assert float(t["amount"]) >= 500


class TestSummaryAndAnalytics:
    def test_summary(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"], amount=2000, t_type="income"), headers=auth_headers)
        client.post("/transactions/", json=make_transaction(account["id"], amount=800, t_type="expense"), headers=auth_headers)
        res = client.get("/transactions/summary", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_income"] == 2000.0
        assert data["total_expense"] == 800.0
        assert data["balance"] == 1200.0

    def test_category_breakdown(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"], amount=300, category="Food"), headers=auth_headers)
        client.post("/transactions/", json=make_transaction(account["id"], amount=500, category="Rent"), headers=auth_headers)
        res = client.get("/transactions/categories?transaction_type=expense", headers=auth_headers)
        assert res.status_code == 200
        categories = [r["category"] for r in res.json()]
        assert "Food" in categories
        assert "Rent" in categories

    def test_monthly_trends(self, client, auth_headers, account):
        client.post("/transactions/", json=make_transaction(account["id"], amount=1000, t_type="income"), headers=auth_headers)
        year = datetime.utcnow().year
        res = client.get(f"/transactions/trends/{year}", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) == 12  # all 12 months returned


class TestUpdateDeleteTransaction:
    def test_update_transaction(self, client, auth_headers, account):
        t = client.post("/transactions/", json=make_transaction(account["id"]), headers=auth_headers).json()
        res = client.patch(f"/transactions/{t['id']}", json={"amount": 999}, headers=auth_headers)
        assert res.status_code == 200
        assert float(res.json()["amount"]) == 999

    def test_delete_transaction(self, client, auth_headers, account):
        t = client.post("/transactions/", json=make_transaction(account["id"]), headers=auth_headers).json()
        res = client.delete(f"/transactions/{t['id']}", headers=auth_headers)
        assert res.status_code == 200
        gone = client.get(f"/transactions/{t['id']}", headers=auth_headers)
        assert gone.status_code == 404
