import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from models.booking import BookingStatus
import uuid


def test_create_booking_success(client, create_regular_user, create_service, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}


    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "service_id": str(create_service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    response = client.post("/bookings/", json=booking_data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["service_id"] == str(create_service.id)
    assert data["user_id"] == str(create_regular_user.id)
    assert data["status"] == BookingStatus.PENDING
    assert "id" in data


def test_create_booking_conflict(client, create_regular_user, create_service, create_booking, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}


    booking_data = {
        "service_id": str(create_service.id),
        "start_time": create_booking.start_time.isoformat(),
        "end_time": create_booking.end_time.isoformat()
    }

    response = client.post("/bookings/", json=booking_data, headers=headers)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "conflicts with existing booking" in response.json()["detail"]


def test_create_booking_past_time(client, create_service, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}


    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "service_id": str(create_service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    response = client.post("/bookings/", json=booking_data, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot book in the past" in response.json()["detail"]


def test_create_booking_invalid_service(client, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "service_id": str(uuid.uuid4()),  # Random UUID
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    response = client.post("/bookings/", json=booking_data, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Service not found" in response.json()["detail"]


def test_create_booking_without_auth(client, create_service):
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "service_id": str(create_service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    response = client.post("/bookings/", json=booking_data)

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


def test_get_user_bookings(client, create_booking, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/bookings/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(create_booking.id)


def test_admin_get_all_bookings(client, create_booking, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/bookings/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


def test_get_booking_by_id_owner(client, create_booking, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(f"/bookings/{create_booking.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(create_booking.id)


def test_get_booking_by_id_admin(client, create_booking, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(f"/bookings/{create_booking.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(create_booking.id)


def test_get_booking_unauthorized(client, create_booking, create_admin_user, admin_user_data):
    other_user_data = {
        "name": "Other User",
        "email": "other@test.com",
        "password": "password123"
    }
    client.post("/auth/register", json=other_user_data)


    login_response = client.post("/auth/login", json={
        "email": "other@test.com",
        "password": "password123"
    })
    other_token = login_response.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {other_token}"}

    response = client.get(f"/bookings/{create_booking.id}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_booking_reschedule(client, create_booking, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}


    new_start = datetime.now(timezone.utc) + timedelta(days=2)
    new_end = new_start + timedelta(hours=2)

    update_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }

    response = client.patch(f"/bookings/{create_booking.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["start_time"] != create_booking.start_time.isoformat()


def test_update_booking_cancel(client, create_booking, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    update_data = {
        "status": BookingStatus.CANCELLED
    }

    response = client.patch(f"/bookings/{create_booking.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == BookingStatus.CANCELLED


def test_admin_update_booking_status(client, create_booking, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    update_data = {
        "status": BookingStatus.CONFIRMED
    }

    response = client.patch(f"/bookings/{create_booking.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == BookingStatus.CONFIRMED


def test_delete_booking_owner(client, create_booking, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.delete(f"/bookings/{create_booking.id}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_booking_admin(client, create_booking, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/bookings/{create_booking.id}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_bookings_with_filters(client, create_booking, admin_token):

    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/bookings/?status=pending", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for booking in data:
        assert booking["status"] == BookingStatus.PENDING


def test_booking_validation_end_before_start(client, create_service, user_token):

    headers = {"Authorization": f"Bearer {user_token}"}

    start_time = datetime.now(timezone.utc) + timedelta(days=1, hours=2)
    end_time = datetime.now(timezone.utc) + timedelta(days=1, hours=1)  # Before start

    booking_data = {
        "service_id": str(create_service.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    response = client.post("/bookings/", json=booking_data, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY