# BookIt API

A production-ready REST API for a simple bookings platform. Users can browse services, make bookings, and leave reviews. Admins manage users, services, and bookings with full administrative controls.

## Live Deployment

- **Base URL:** https://book-it-api-23p1.onrender.com/
- **API Documentation:** https://book-it-api-23p1.onrender.com/docs
- **Alternative Docs:** https://book-it-api-23p1.onrender.com/redoc

## Architecture Overview

### Technology Stack
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** bcrypt
- **Database Migrations:** Alembic
- **Deployment:** Render.com
- **Testing:** pytest

### Database Choice: PostgreSQL

**I Chose PostgreSQL over MongoDB for the following reasons:**

1. Booking conflicts require strict transactional integrity to prevent double-bookings which mongoDB can not execute effectively
2. There are Clear relationships between users, services, bookings, and reviews benefit from foreign key constraints
3. There are Complex filtering and reporting queries which is more efficient with SQL
4.  Database-level constraints ensure data integrity (unique bookings per service time slot). this is provided with postgres

### Core Architecture

```
├── main.py                 # FastAPI application entry point
├── core/                   # Core configuration
│   ├── database.py         # Database connection and session management
│   └── security.py         # JWT and password hashing utilities
├── models/                 # SQLAlchemy database models
│   ├── user.py            # User model with role-based access
│   ├── service.py         # Service model
│   ├── booking.py         # Booking model with status management
│   └── review.py          # Review model with booking constraints
├── schema/                # Pydantic schemas for validation
├── crud/                  # Database operations layer
├── api/router/           # API route handlers
└── alembic/              # Database migrations
```

## Features

### Authentication & Authorization
- JWT-based authentication with access and refresh tokens
- Role-based access control (User/Admin)
- Secure password hashing with bcrypt
- Token expiration and refresh mechanisms

### Booking System
- **Conflict Detection:** Prevents overlapping bookings for the same service
- **Status Management:** Pending → Confirmed → Completed workflow
- **Time Validation:** Prevents booking in the past
- **User Permissions:** Users manage their own bookings, admins manage all

### Review System
- One review per completed booking
- Rating system (1-5 stars)
- Only booking owners can leave reviews
- Review statistics for services

### Service Management
- Admin-only service creation and management
- Service activation/deactivation
- Price and duration management
- Public service browsing with filtering

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout

### User Management
- `GET /users/me` - Current user profile
- `PATCH /users/me` - Update user profile

### Services
- `GET /services` - List all active services (with filtering)
- `GET /services/{id}` - Get specific service
- `POST /services` - Create service (admin only)
- `PATCH /services/{id}` - Update service (admin only)
- `DELETE /services/{id}` - Delete service (admin only)

### Bookings
- `POST /bookings` - Create booking (with conflict detection)
- `GET /bookings` - List bookings (user: own bookings, admin: all bookings)
- `GET /bookings/{id}` - Get specific booking
- `PATCH /bookings/{id}` - Update booking (owner/admin)
- `DELETE /bookings/{id}` - Delete booking (owner/admin with restrictions)

### Reviews
- `POST /reviews` - Create review (completed bookings only)
- `GET /reviews/{id}` - Get specific review
- `PATCH /reviews/{id}` - Update review (owner only)
- `DELETE /reviews/{id}` - Delete review (owner/admin)
- `GET /reviews/services/{service_id}/reviews` - Get service reviews
- `GET /reviews/services/{service_id}/stats` - Get service review statistics

## Test Accounts

The production database is pre-populated with test data for immediate testing:

### Admin Account
- **Email:** admin@gmail.com
- **Password:** admin123
- **Capabilities:** Full system access, can manage all entities

### User Accounts
- **Email:** john.doe@gmail.com, jane.smith@gmail.com, bob.johnson@gmail.com
- **Password:** 123456
- **Capabilities:** Manage own bookings and reviews

### Pre-populated Data
- 8 services with varying prices and durations
- 10 bookings across different statuses (completed, confirmed, pending, cancelled)
- 3 reviews for completed bookings
- Realistic conflict scenarios for testing

## Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/STORMGAMER0/book-it.git
   cd book-it
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE book_it;
   ```

5. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/book_it_dev
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRES_MINUTES=30
   JWT_REFRESH_TOKEN_EXPIRES_DAYS=7
   DEBUG=True
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Seed the database (optional)**
   ```bash
   python seed_database.py
   ```

8. **Start the development server**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Yes | - |
| `JWT_ALGORITHM` | Algorithm for JWT encoding | No | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | Access token expiration time | No | 30 |
| `JWT_REFRESH_TOKEN_EXPIRES_DAYS` | Refresh token expiration time | No | 7 |
| `DEBUG` | Enable debug mode | No | False |
| `LOG_LEVEL` | Logging level | No | INFO |
| `DB_POOL_SIZE` | Database connection pool size | No | 10 |
| `DB_MAX_OVERFLOW` | Maximum connection overflow | No | 20 |
| `DB_ECHO` | Log SQL queries | No | False |

## Testing

The project includes comprehensive test coverage with pytest:

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx faker

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_auth.py -v        # Authentication tests
pytest tests/test_bookings.py -v    # Booking system tests
```

### Test Coverage

- **Authentication Tests:** Registration, login, JWT handling, role-based access
- **Booking Conflict Tests:** Comprehensive overlap detection scenarios
- **Permission Tests:** User vs admin access control
- **Status Management Tests:** Booking lifecycle and state transitions
- **Integration Tests:** End-to-end workflow testing

### Test Database

Tests use a separate PostgreSQL database (`book_it_test`) with automatic cleanup between tests.

## Production Deployment

### Render.com Deployment

The application is deployed on Render.com with the following configuration:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
alembic upgrade head && python seed_database.py && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Database

Production uses a managed PostgreSQL instance on Render with:
- Automatic backups
- Connection pooling
- SSL encryption
- High availability

### Environment Configuration

All sensitive configuration is managed through environment variables with no secrets committed to the repository.

## Key Business Rules

### Booking Conflicts
- **409 Conflict** returned when bookings overlap for the same service
- Only considers PENDING and CONFIRMED bookings for conflicts
- CANCELLED bookings don't prevent new bookings
- Adjacent bookings (touching times) are allowed

### Permissions
- **Users:** Can CRUD their own bookings and reviews
- **Admins:** Can view all bookings, change booking status, manage services
- **401 Unauthorized:** Missing or invalid authentication
- **403 Forbidden:** Valid authentication but insufficient permissions

### Review Constraints
- Only for COMPLETED bookings
- One review per booking (unique constraint)
- Only the booking owner can create reviews
- Rating must be between 1-5 stars

### Time Validation
- All bookings must be in the future
- End time must be after start time
- Timezone-aware datetime handling throughout

## Error Handling

The API implements comprehensive error handling with appropriate HTTP status codes:

- **200 OK:** Successful GET, PATCH operations
- **201 Created:** Successful POST operations
- **204 No Content:** Successful DELETE operations
- **400 Bad Request:** Validation errors, business rule violations
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **409 Conflict:** Booking conflicts, duplicate data
- **422 Unprocessable Entity:** Request validation errors
- **500 Internal Server Error:** Unexpected server errors

## Security Considerations

- JWT tokens with configurable expiration
- Password hashing with bcrypt (cost factor 12)
- SQL injection prevention through ORM
- Input validation with Pydantic schemas
- Rate limiting ready for production
- CORS configuration for web clients
- Environment-based secret management


**Built with FastAPI, PostgreSQL, and deployed on Render.com**