import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from main import app
from core.database import get_db, Base
from models.user import User, Roles
from models.service import Service
from models.booking import Booking, BookingStatus
from models.review import Review
from core.security import hash_password
import uuid
from datetime import datetime, timedelta, timezone

load_dotenv()


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:3691@localhost:5432/book_it_test")

engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def setup_database():

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():

    db = TestingSessionLocal()
    try:
        yield db
    finally:

        try:
            for table in reversed(Base.metadata.sorted_tables):
                db.execute(table.delete())
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()

@pytest.fixture
def client(setup_database):

    return TestClient(app)

@pytest.fixture
def regular_user_data():

    import time
    timestamp = str(int(time.time() * 1000))  # Microsecond timestamp
    return {
        "name": "Test User",
        "email": f"user{timestamp}@test.com",
        "password": "testpassword123"
    }

@pytest.fixture
def admin_user_data():

    import time
    timestamp = str(int(time.time() * 1000))
    return {
        "name": "Admin User",
        "email": f"admin{timestamp}@test.com",
        "password": "adminpassword123"
    }
@pytest.fixture
def service_data():

    return {
        "title": "Test Service",
        "description": "A test service for automated testing",
        "price": "99.99",
        "duration_minutes": 60,
        "is_active": True
    }

@pytest.fixture
def create_regular_user(db, regular_user_data):

    user = User(
        id=uuid.uuid4(),
        name=regular_user_data["name"],
        email=regular_user_data["email"],
        password_hash=hash_password(regular_user_data["password"]),
        role=Roles.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def create_admin_user(db, admin_user_data):

    user = User(
        id=uuid.uuid4(),
        name=admin_user_data["name"],
        email=admin_user_data["email"],
        password_hash=hash_password(admin_user_data["password"]),
        role=Roles.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def create_service(db, service_data):

    service = Service(
        id=uuid.uuid4(),
        title=service_data["title"],
        description=service_data["description"],
        price=service_data["price"],
        duration_minutes=service_data["duration_minutes"],
        is_active=service_data["is_active"]
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@pytest.fixture
def user_token(client, create_regular_user, regular_user_data):

    login_data = {
        "email": regular_user_data["email"],
        "password": regular_user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["tokens"]["access_token"]

@pytest.fixture
def admin_token(client, create_admin_user, admin_user_data):

    login_data = {
        "email": admin_user_data["email"],
        "password": admin_user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["tokens"]["access_token"]

@pytest.fixture
def auth_headers(user_token):

    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_headers(admin_token):

    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def create_booking(db, create_regular_user, create_service):

    booking = Booking(
        id=uuid.uuid4(),
        user_id=create_regular_user.id,
        service_id=create_service.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
        status=BookingStatus.PENDING
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@pytest.fixture
def create_completed_booking(db, create_regular_user, create_service):

    booking = Booking(
        id=uuid.uuid4(),
        user_id=create_regular_user.id,
        service_id=create_service.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
        status=BookingStatus.COMPLETED
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking