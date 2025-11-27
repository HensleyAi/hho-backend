from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

class TransactionBase(BaseModel):
    date: Optional[date]
    description: Optional[str]
    amount: float
    category: Optional[str] = None
    is_recurring: bool = False

class TransactionCreate(TransactionBase):
    statement_id: int
    account_id: int

class Transaction(TransactionBase):
    id: int
    statement_id: int
    account_id: int

    class Config:
        orm_mode = True

class StatementBase(BaseModel):
    account_id: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    original_filename: str

class StatementCreate(StatementBase):
    pass

class Statement(StatementBase):
    id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True

class AccountBase(BaseModel):
    name: str
    type: Optional[str] = None

class AccountCreate(AccountBase):
    user_id: int

class Account(AccountBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class IncomeEventBase(BaseModel):
    date: date
    description: Optional[str] = None
    amount: float
    source_type: Optional[str] = None

class IncomeEventCreate(IncomeEventBase):
    user_id: int

class IncomeEvent(IncomeEventBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class MonthlySummary(BaseModel):
    month_start: date
    month_end: date
    total_income: float
    total_expenses: float
    net: float
    recurring_expenses: float
    variable_expenses: float

class ProjectionRequest(BaseModel):
    user_id: int
    months_ahead: int = 3

class ProjectionResult(BaseModel):
    period_start: date
    period_end: date
    projected_income: float
    projected_expenses: float
    projected_net: float

class AIInsightRequest(BaseModel):
    user_id: int
    period_start: date
    period_end: date

class AIInsightResult(BaseModel):
    summary: str
