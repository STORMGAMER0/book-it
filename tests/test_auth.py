import pytest
from fastapi import status


class TestAuthRegistration:


    def test_register_user_success(self, client, regular_user_data):

        response = client.post("/auth/register", json=regular_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == regular_user_data["email"]
        assert data["name"] == regular_user_data["name"]
        assert data["role"] == "user"
        assert "password" not in data

    def test_register_duplicate_email(self, client, regular_user_data):

        client.post("/auth/register", json=regular_user_data)


        response = client.post("/auth/register", json=regular_user_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):

        invalid_data = {
            "name": "Test User",
            "email": "not-an-email",
            "password": "testpassword123"
        }
        response = client.post("/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client):

        invalid_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "short"
        }
        response = client.post("/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:


    def test_login_success(self, client, create_regular_user, regular_user_data):

        login_data = {
            "email": regular_user_data["email"],
            "password": regular_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert data["tokens"]["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == regular_user_data["email"]

    def test_login_wrong_password(self, client, create_regular_user, regular_user_data):

        login_data = {
            "email": regular_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect email or password" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):

        login_data = {
            "email": "nonexistent@test.com",
            "password": "somepassword"
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_email_format(self, client):

        login_data = {
            "email": "not-an-email",
            "password": "somepassword"
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthProtectedRoutes:


    def test_access_protected_route_with_valid_token(self, client, auth_headers):

        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_access_protected_route_without_token(self, client):

        response = client.get("/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_access_protected_route_with_invalid_token(self, client):

        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_route_with_malformed_token(self, client):

        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthRoleBasedAccess:

    def test_admin_route_with_admin_token(self, client, admin_headers, service_data):

        response = client.post("/services", json=service_data, headers=admin_headers)

        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_route_with_user_token(self, client, auth_headers, service_data):

        response = client.post("/services", json=service_data, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "admin access required" in response.json()["detail"].lower()

    def test_user_route_with_user_token(self, client, auth_headers):

        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK


class TestAuthTokenRefresh:


    def test_refresh_token_success(self, client, create_regular_user, regular_user_data):


        login_data = {
            "email": regular_user_data["email"],
            "password": regular_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        refresh_token = login_response.json()["tokens"]["refresh_token"]


        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):

        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid refresh token" in response.json()["detail"].lower()


class TestAuthLogout:


    def test_logout_success(self, client, auth_headers):

        response = client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "logout successful" in response.json()["message"].lower()

    def test_logout_without_token(self, client):

        response = client.post("/auth/logout")

        assert response.status_code == status.HTTP_403_FORBIDDEN