import pytest
from fastapi import status
from decimal import Decimal
import uuid


def test_create_service_admin(client, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    service_data = {
        "title": "Test Service",
        "description": "A test service description",
        "price": "99.99",
        "duration_minutes": 60,
        "is_active": True
    }

    response = client.post("/services/", json=service_data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == service_data["title"]
    assert data["description"] == service_data["description"]
    assert float(data["price"]) == float(service_data["price"])
    assert data["duration_minutes"] == service_data["duration_minutes"]
    assert data["is_active"] == service_data["is_active"]
    assert "id" in data


def test_create_service_regular_user_forbidden(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    service_data = {
        "title": "Test Service",
        "description": "A test service description",
        "price": "99.99",
        "duration_minutes": 60
    }

    response = client.post("/services/", json=service_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_service_without_auth(client):

    service_data = {
        "title": "Test Service",
        "description": "A test service description",
        "price": "99.99",
        "duration_minutes": 60
    }

    response = client.post("/services/", json=service_data)

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


def test_create_service_validation_errors(client, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}


    service_data = {
        "title": "",
        "description": "A test service description",
        "price": "99.99",
        "duration_minutes": 60
    }

    response = client.post("/services/", json=service_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


    service_data = {
        "title": "Valid Title",
        "description": "A test service description",
        "price": "-10.00",
        "duration_minutes": 60
    }

    response = client.post("/services/", json=service_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


    service_data = {
        "title": "Valid Title",
        "description": "A test service description",
        "price": "99.99",
        "duration_minutes": 500
    }

    response = client.post("/services/", json=service_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_service_by_id_public(client, create_service):

    response = client.get(f"/services/{create_service.id}")


    assert response.status_code == status.HTTP_200_OK


def test_get_service_by_id_not_found(client):

    fake_id = str(uuid.uuid4())
    response = client.get(f"/services/{fake_id}")


    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_services_public(client, create_service):

    response = client.get("/services/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_services_with_search(client, create_service):

    response = client.get("/services?q=Test")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_services_with_price_filter(client, create_service):

    response = client.get("/services?price_min=50&price_max=150")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_update_service_admin(client, create_service, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    update_data = {
        "title": "Updated Service Title",
        "price": "149.99"
    }

    response = client.patch(f"/services/{create_service.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == update_data["title"]
    assert float(data["price"]) == float(update_data["price"])


def test_update_service_regular_user_forbidden(client, create_service, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    update_data = {
        "title": "Hacker Title"
    }

    response = client.patch(f"/services/{create_service.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_service_not_found(client, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_id = str(uuid.uuid4())

    update_data = {
        "title": "Updated Title"
    }

    response = client.patch(f"/services/{fake_id}", json=update_data, headers=headers)


    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_service_admin(client, create_service, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/services/{create_service.id}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_service_regular_user_forbidden(client, create_service, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.delete(f"/services/{create_service.id}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_deactivate_service(client, create_service, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    update_data = {
        "is_active": False
    }

    response = client.patch(f"/services/{create_service.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False