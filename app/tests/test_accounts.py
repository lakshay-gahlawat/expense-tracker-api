class TestCreateAccount:
    def test_create_success(self, client, auth_headers):
        res = client.post("/accounts/", json={"name": "Savings"}, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()["name"] == "Savings"

    def test_create_requires_auth(self, client):
        res = client.post("/accounts/", json={"name": "Savings"})
        assert res.status_code == 403


class TestGetAccounts:
    def test_list_accounts(self, client, auth_headers, account):
        res = client.get("/accounts/", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        assert "items" in data
        assert "pages" in data

    def test_filter_by_name(self, client, auth_headers):
        client.post("/accounts/", json={"name": "Holiday Fund"}, headers=auth_headers)
        client.post("/accounts/", json={"name": "Rent"}, headers=auth_headers)
        res = client.get("/accounts/?name=Holiday", headers=auth_headers)
        assert res.status_code == 200
        assert all("Holiday" in a["name"] for a in res.json()["items"])

    def test_pagination(self, client, auth_headers):
        for i in range(5):
            client.post("/accounts/", json={"name": f"Account {i}"}, headers=auth_headers)
        res = client.get("/accounts/?page=1&limit=2", headers=auth_headers)
        assert len(res.json()["items"]) == 2

    def test_cannot_see_other_users_accounts(self, client, auth_headers, account):
        # Register a second user
        client.post("/users/register", json={"email": "user2@x.com", "password": "pass123"})
        login = client.post("/users/login", json={"email": "user2@x.com", "password": "pass123"})
        headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}
        res = client.get("/accounts/", headers=headers2)
        assert res.json()["total"] == 0


class TestAccountSummary:
    def test_summary_empty(self, client, auth_headers, account):
        res = client.get(f"/accounts/summary/{account['id']}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_income"] == 0.0
        assert data["total_expense"] == 0.0
        assert data["balance"] == 0.0

    def test_summary_with_transactions(self, client, auth_headers, account):
        from datetime import datetime
        ts = datetime.utcnow().isoformat()
        client.post("/transactions/", json={
            "account_id": account["id"], "amount": 1000, "transaction_type": "income",
            "category": "Salary", "date": ts,
        }, headers=auth_headers)
        client.post("/transactions/", json={
            "account_id": account["id"], "amount": 300, "transaction_type": "expense",
            "category": "Food", "date": ts,
        }, headers=auth_headers)
        res = client.get(f"/accounts/summary/{account['id']}", headers=auth_headers)
        data = res.json()
        assert data["total_income"] == 1000.0
        assert data["total_expense"] == 300.0
        assert data["balance"] == 700.0


class TestUpdateDeleteAccount:
    def test_update_name(self, client, auth_headers, account):
        res = client.patch(f"/accounts/{account['id']}", json={"name": "Updated"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "Updated"

    def test_delete_account(self, client, auth_headers, account):
        res = client.delete(f"/accounts/{account['id']}", headers=auth_headers)
        assert res.status_code == 200
        gone = client.get(f"/accounts/{account['id']}", headers=auth_headers)
        assert gone.status_code == 404
