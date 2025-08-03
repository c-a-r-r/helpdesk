import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # Default to SQLite for development

if DB_TYPE.lower() == "sqlite":
    # SQLite configuration (for development)
    DB_PATH = os.getenv("DB_PATH", "./helpdesk_crm.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    # Create SQLAlchemy engine for SQLite
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # MariaDB/MySQL configuration (for production)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "helpdesk_crm")

    # MariaDB connection string
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Create SQLAlchemy engine
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        pool_pre_ping=True,
        pool_recycle=300
    )

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
