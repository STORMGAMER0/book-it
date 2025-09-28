import pytest
from fastapi import status
import uuid


def test_get_current_user_profile(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/users/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "role" in data
    assert "created_at" in data
    assert "password" not in data


def test_get_current_user_profile_without_auth(client):

    response = client.get("/users/me")

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


def test_get_current_user_profile_invalid_token(client):

    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/users/me", headers=headers)

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


def test_update_user_profile_name(client, create_regular_user, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {
        "name": "Updated Name"
    }

    response = client.patch("/users/me", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == create_regular_user.email  # Should remain unchanged


def test_update_user_profile_email(client, create_regular_user, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {
        "email": "newemail@example.com"
    }

    response = client.patch("/users/me", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "newemail@example.com"
    assert data["name"] == create_regular_user.name  # Should remain unchanged


def test_update_user_profile_both_fields(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {
        "name": "New Name",
        "email": "newemail2@example.com"
    }

    response = client.patch("/users/me", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name"
    assert data["email"] == "newemail2@example.com"


def test_update_user_profile_empty_data(client, create_regular_user, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.patch("/users/me", json={}, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == create_regular_user.name
    assert data["email"] == create_regular_user.email


def test_update_user_profile_duplicate_email(client, create_regular_user, create_admin_user, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    # Try to update to the admin user's email
    update_data = {
        "email": create_admin_user.email
    }

    response = client.patch("/users/me", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_user_profile_without_auth(client):

    update_data = {
        "name": "Hacker Name"
    }

    response = client.patch("/users/me", json=update_data)

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


def test_update_user_profile_invalid_email_format(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {
        "email": "not-an-email"
    }

    response = client.patch("/users/me", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_user_profile_empty_name(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {
        "name": ""
    }

    response = client.patch("/users/me", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_by_id_public(client, create_regular_user):

    response = client.get(f"/users/{create_regular_user.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(create_regular_user.id)
    assert data["email"] == create_regular_user.email


def test_get_user_by_id_not_found(client):

    fake_id = str(uuid.uuid4())
    response = client.get(f"/users/{fake_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_by_email_public(client, create_regular_user):

    response = client.get(f"/users/email/{create_regular_user.email}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == create_regular_user.email


def test_get_user_by_email_not_found(client):

    response = client.get("/users/email/nonexistent@example.com")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_user_profile_after_update_persists(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}


    update_data = {
        "name": "Persistent Name",
        "email": "persistent@example.com"
    }

    update_response = client.patch("/users/me", json=update_data, headers=headers)
    assert update_response.status_code == status.HTTP_200_OK

    
    get_response = client.get("/users/me", headers=headers)
    assert get_response.status_code == status.HTTP_200_OK

    data = get_response.json()
    assert data["name"] == "Persistent Name"
    assert data["email"] == "persistent@example.com"