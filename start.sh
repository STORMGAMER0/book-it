#!/bin/bash

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Seed the database with sample data
echo "Seeding database with sample data..."
python seed_database.py

# Start the application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port $PORT