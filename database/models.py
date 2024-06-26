# database/models.py
from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FinancialData(Base):
    __tablename__ = 'financial_data'
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    revenue = Column(Float)
    expenses = Column(Float)
    profit = Column(Float)
