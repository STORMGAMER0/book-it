import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE URL NOT FOUND")

POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
DB_ECHO = bool(os.getenv("DB_ECHO", False))

#pool_pre_ping prevents database connections from going stale. it does this by sending a tiny query before a connection is used. if it fails, it creates a new connection. if it doesnt, it uses the same connection
#pool_recycle restarts/refreshes the connection. for this setting, it refreshes it every 1 hour
#echo logs sql queries to console
engine = create_engine(DATABASE_URL,pool_size=POOL_SIZE,max_overflow=MAX_OVERFLOW,echo=DB_ECHO,pool_pre_ping = True, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("database tables created successfully✅")

def drop_tables():
    Base.metadata.drop_all(bind=engine)



