import pytest


class TestRegister:
    def test_register_success(self, client):
        res = client.post("/users/register", json={"email": "new@example.com", "password": "pass123"})
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "new@example.com"
        assert "hashed_password" not in data  # must never be exposed
        assert "id" in data

    def test_register_duplicate_email(self, client):
        payload = {"email": "dup@example.com", "password": "pass123"}
        client.post("/users/register", json=payload)
        res = client.post("/users/register", json=payload)
        assert res.status_code == 409

    def test_register_missing_fields(self, client):
        res = client.post("/users/register", json={"email": "x@x.com"})
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user):
        res = client.post("/users/login", json=registered_user)
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert res.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        res = client.post("/users/login", json={"email": registered_user["email"], "password": "wrong"})
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post("/users/login", json={"email": "ghost@x.com", "password": "pass"})
        assert res.status_code == 401


class TestMe:
    def test_get_me(self, client, auth_headers):
        res = client.get("/users/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["email"] == "test@example.com"

    def test_get_me_no_token(self, client):
        res = client.get("/users/me")
        assert res.status_code == 403

    def test_get_me_invalid_token(self, client):
        res = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
        assert res.status_code == 401


class TestUpdateUser:
    def test_update_email(self, client, auth_headers):
        me = client.get("/users/me", headers=auth_headers).json()
        res = client.patch(f"/users/{me['id']}", json={"email": "updated@example.com"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["email"] == "updated@example.com"

    def test_cannot_update_other_user(self, client, auth_headers):
        other = client.post("/users/register", json={"email": "other@x.com", "password": "pass123"}).json()
        res = client.patch(f"/users/{other['id']}", json={"email": "hack@x.com"}, headers=auth_headers)
        assert res.status_code == 403
