from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)

    accounts = relationship("Account", back_populates="user")
    income_events = relationship("IncomeEvent", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)  # checking, savings, credit, etc.

    user = relationship("User", back_populates="accounts")
    statements = relationship("Statement", back_populates="account")

class Statement(Base):
    __tablename__ = "statements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    original_filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="statements")
    transactions = relationship("Transaction", back_populates="statement")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)  # negative = debit, positive = credit
    category = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)

    statement = relationship("Statement", back_populates="transactions")

class IncomeEvent(Base):
    __tablename__ = "income_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    source_type = Column(String, nullable=True)  # closing, salary, commission, etc.

    user = relationship("User", back_populates="income_events")
