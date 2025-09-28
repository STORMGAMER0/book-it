# Create a simple script: create_all_tables.py
from core.database import engine, Base
from models.user import User
from models.service import Service
from models.booking import Booking  # Only if you added it
from models.review import Review    # Only if you added it

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")