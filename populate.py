# populate_database.py
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from database.models import Base, FinancialData
from config import Config

# Connect to the database
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
print(f"Database Engine: {engine}")

try:
    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    # Read data from CSV
    data = pd.read_csv('data/financial_data.csv')
    print("Data to be inserted:")
    print(data)

    # Insert data into the database
    data.to_sql('financial_data', engine, if_exists='replace', index=False)
    print("Data inserted successfully.")

except SQLAlchemyError as e:
    print(f"Error occurred: {e}")
