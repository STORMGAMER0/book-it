import os
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from core.database import SessionLocal, create_tables
from models.user import User, Roles
from models.service import Service
from models.booking import Booking, BookingStatus
from models.review import Review
from core.security import hash_password


def seed_database():
    """Populate database with sample data for testing"""

    # Create tables first
    create_tables()

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already has data. Skipping seed.")
            return

        print("Seeding database with sample data...")

        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            name="Admin User",
            email="admin@gmail.com",
            password_hash=hash_password("admin123"),
            role=Roles.ADMIN
        )
        db.add(admin_user)

        # Create regular users 
        users = []
        user_data = [
            ("John Doe", "john.doe@gmail.com", "123456"),
            ("Jane Smith", "jane.smith@gmail.com", "123456"),
            ("Bob Johnson", "bob.johnson@gmail.com", "123456"),
            ("Alice Brown", "alice.brown@gmail.com", "123456"),
            ("Charlie Wilson", "charlie.wilson@gmail.com", "123456")
        ]

        for name, email, password in user_data:
            user = User(
                id=uuid.uuid4(),
                name=name,
                email=email,
                password_hash=hash_password(password),
                role=Roles.USER
            )
            users.append(user)
            db.add(user)

        # Create services
        services = []
        service_data = [
            ("Web Development Consultation", "Professional web development consultation and planning", "150.00", 90),
            ("Mobile App Design", "Complete mobile application design and prototyping", "200.00", 120),
            ("Database Architecture Review", "Comprehensive database design and optimization review", "180.00", 75),
            ("API Development Workshop", "Hands-on API development training session", "120.00", 60),
            ("Cloud Migration Planning", "Strategic planning for cloud infrastructure migration", "250.00", 150),
            ("Security Audit", "Complete security assessment of your application", "300.00", 180),
            ("Performance Optimization", "Application performance analysis and improvement", "175.00", 90),
            ("Code Review Session", "Detailed code review and best practices consultation", "100.00", 45)
        ]

        for title, description, price, duration in service_data:
            service = Service(
                id=uuid.uuid4(),
                title=title,
                description=description,
                price=price,
                duration_minutes=duration,
                is_active=True
            )
            services.append(service)
            db.add(service)

        # Commit users and services first
        db.commit()
        db.refresh(admin_user)
        for user in users:
            db.refresh(user)
        for service in services:
            db.refresh(service)

        # Create bookings with various statuses and times
        bookings = []
        base_date = datetime.now(timezone.utc)

        booking_scenarios = [
            # Past completed bookings
            (users[0], services[0], base_date - timedelta(days=5),
             base_date - timedelta(days=5) + timedelta(minutes=90), BookingStatus.COMPLETED),
            (users[1], services[1], base_date - timedelta(days=3),
             base_date - timedelta(days=3) + timedelta(minutes=120), BookingStatus.COMPLETED),
            (users[2], services[2], base_date - timedelta(days=2),
             base_date - timedelta(days=2) + timedelta(minutes=75), BookingStatus.COMPLETED),

            # Current/recent confirmed bookings
            (users[0], services[3], base_date + timedelta(hours=2), base_date + timedelta(hours=3),
             BookingStatus.CONFIRMED),
            (users[3], services[4], base_date + timedelta(days=1),
             base_date + timedelta(days=1) + timedelta(minutes=150), BookingStatus.CONFIRMED),
            (users[1], services[5], base_date + timedelta(days=2),
             base_date + timedelta(days=2) + timedelta(minutes=180), BookingStatus.CONFIRMED),

            # Pending bookings
            (users[2], services[6], base_date + timedelta(days=3),
             base_date + timedelta(days=3) + timedelta(minutes=90), BookingStatus.PENDING),
            (users[4], services[7], base_date + timedelta(days=4),
             base_date + timedelta(days=4) + timedelta(minutes=45), BookingStatus.PENDING),
            (users[3], services[0], base_date + timedelta(days=5),
             base_date + timedelta(days=5) + timedelta(minutes=90), BookingStatus.PENDING),

            # One cancelled booking
            (users[4], services[1], base_date + timedelta(days=6),
             base_date + timedelta(days=6) + timedelta(minutes=120), BookingStatus.CANCELLED),
        ]

        for user, service, start_time, end_time, status in booking_scenarios:
            booking = Booking(
                id=uuid.uuid4(),
                user_id=user.id,
                service_id=service.id,
                start_time=start_time,
                end_time=end_time,
                status=status
            )
            bookings.append(booking)
            db.add(booking)

        db.commit()
        for booking in bookings:
            db.refresh(booking)

        # Create reviews for completed bookings
        completed_bookings = [b for b in bookings if b.status == BookingStatus.COMPLETED]

        review_data = [
            (5, "Excellent consultation! Very knowledgeable and helpful."),
            (4, "Great mobile app design session. Learned a lot and got valuable insights."),
            (5, "Outstanding database review. Identified several optimization opportunities."),
        ]

        for i, (rating, comment) in enumerate(review_data):
            if i < len(completed_bookings):
                review = Review(
                    id=uuid.uuid4(),
                    booking_id=completed_bookings[i].id,
                    rating=rating,
                    comment=comment
                )
                db.add(review)

        db.commit()

        print("✅ Database seeded successfully!")
        print("\n📊 Created:")
        print(f"  - 1 Admin user (admin@bookit.com / admin123)")
        print(f"  - {len(users)} Regular users")
        print(f"  - {len(services)} Services")
        print(f"  - {len(bookings)} Bookings (various statuses)")
        print(f"  - {len(review_data)} Reviews")
        print("\n🔐 Test Accounts:")
        print("  Admin: admin@bookit.com / admin123")
        print("  Users: john@example.com, jane@example.com, bob@example.com / password123")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()