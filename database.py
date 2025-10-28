import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Construct the database URL
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker object
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_table_schema(table_name: str):
    """
    Introspects the schema of a given table.
    Returns a dictionary with column names and their types.
    """
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    schema = {column['name']: str(column['type']) for column in columns}
    return schema

def get_all_table_names():
    """
    Returns a list of all table names in the connected database.
    """
    inspector = inspect(engine)
    return inspector.get_table_names()

def execute_sql_query(sql_query: str):
    """
    Executes a raw SQL query and returns the results.
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))
        if result.returns_rows:
            return [row._asdict() for row in result.fetchall()]
        return {"message": "Query executed successfully, no rows returned."}

