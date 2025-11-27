from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
from decimal import Decimal
import io

from .database import Base, engine, get_db
from . import models, schemas
from .ai import get_ai_insights

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hensley Home Office Backend v1")

# Allow all origins for now; tighten later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user_id() -> int:
    # For v1 we assume a single user with id=1.
    # Later we can replace this with real auth.
    return 1

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.get("/accounts/", response_model=List[schemas.Account])
def list_accounts(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Account).filter(models.Account.user_id == user_id).all()

@app.post("/statements/upload", response_model=schemas.Statement)
async def upload_statement(
    account_id: int,
    period_start: date | None = None,
    period_end: date | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id()

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    db_statement = models.Statement(
        user_id=user_id,
        account_id=account_id,
        period_start=period_start,
        period_end=period_end,
        original_filename=file.filename,
        uploaded_at=datetime.utcnow(),
    )
    db.add(db_statement)
    db.commit()
    db.refresh(db_statement)

    # TODO: extract text from PDF and call AI parser to create Transaction rows.
    # For now this endpoint only stores the statement metadata.
    return db_statement

@app.get("/statements/", response_model=List[schemas.Statement])
def list_statements(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Statement)
        .filter(models.Statement.user_id == user_id)
        .order_by(models.Statement.uploaded_at.desc())
        .all()
    )

@app.post("/transactions/bulk", response_model=List[schemas.Transaction])
def create_transactions_bulk(
    items: List[schemas.TransactionCreate],
    db: Session = Depends(get_db),
):
    db_items = [models.Transaction(**item.dict()) for item in items]
    db.add_all(db_items)
    db.commit()
    for item in db_items:
        db.refresh(item)
    return db_items

@app.get("/summary/monthly", response_model=schemas.MonthlySummary)
def monthly_summary(
    user_id: int,
    month_start: date,
    month_end: date,
    db: Session = Depends(get_db),
):
    qs = (
        db.query(models.Transaction)
        .join(models.Statement, models.Transaction.statement_id == models.Statement.id)
        .filter(
            models.Statement.user_id == user_id,
            models.Transaction.date >= month_start,
            models.Transaction.date <= month_end,
        )
    )

    transactions = qs.all()
    total_income = Decimal("0.00")
    total_expenses = Decimal("0.00")
    recurring_expenses = Decimal("0.00")
    variable_expenses = Decimal("0.00")

    for t in transactions:
        if t.amount > 0:
            total_income += t.amount
        else:
            total_expenses += t.amount
            if t.is_recurring:
                recurring_expenses += t.amount
            else:
                variable_expenses += t.amount

    net = total_income + total_expenses

    return schemas.MonthlySummary(
        month_start=month_start,
        month_end=month_end,
        total_income=float(total_income),
        total_expenses=float(total_expenses),
        net=float(net),
        recurring_expenses=float(recurring_expenses),
        variable_expenses=float(variable_expenses),
    )

@app.post("/income-events/", response_model=schemas.IncomeEvent)
def create_income_event(
    event: schemas.IncomeEventCreate,
    db: Session = Depends(get_db),
):
    db_event = models.IncomeEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/income-events/", response_model=List[schemas.IncomeEvent])
def list_income_events(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.IncomeEvent)
        .filter(models.IncomeEvent.user_id == user_id)
        .order_by(models.IncomeEvent.date.desc())
        .all()
    )

@app.post("/projections/", response_model=schemas.ProjectionResult)
def create_projection(
    req: schemas.ProjectionRequest,
    db: Session = Depends(get_db),
):
    # Very simple first pass: project using average of last 3 months
    today = date.today()
    # Here we just return a placeholder; real logic will be added later.
    period_start = today
    period_end = date(today.year, min(today.month + req.months_ahead, 12), today.day)

    # TODO: implement projection logic based on past data.
    return schemas.ProjectionResult(
        period_start=period_start,
        period_end=period_end,
        projected_income=0.0,
        projected_expenses=0.0,
        projected_net=0.0,
    )

@app.post("/ai/insights", response_model=schemas.AIInsightResult)
def ai_insights(
    req: schemas.AIInsightRequest,
    db: Session = Depends(get_db),
):
    qs = (
        db.query(models.Transaction)
        .join(models.Statement, models.Transaction.statement_id == models.Statement.id)
        .filter(
            models.Statement.user_id == req.user_id,
            models.Transaction.date >= req.period_start,
            models.Transaction.date <= req.period_end,
        )
    )
    transactions = qs.all()
    summary = get_ai_insights(transactions, req.period_start, req.period_end)
    return schemas.AIInsightResult(summary=summary)
