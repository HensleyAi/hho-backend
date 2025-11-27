from typing import List
from datetime import date
from decimal import Decimal
import openai
from .config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def build_transactions_summary(transactions) -> str:
    lines = []
    for t in transactions:
        lines.append(f"{t.date} | {t.description} | {t.amount} | {t.category} | recurring={t.is_recurring}")
    return "\n".join(lines)

def get_ai_insights(transactions, period_start: date, period_end: date) -> str:
    if not OPENAI_API_KEY:
        return "AI insights are not configured because OPENAI_API_KEY is missing."

    content = f"""
You are an expert financial analyst. The user has the following bank/credit transactions between {period_start} and {period_end}.

Each line: date | description | amount | category | recurring flag (True/False).
Negative amounts are expenses. Positive amounts are income.

Transactions:
{build_transactions_summary(transactions)}

In 3 short sections, explain:
1) What happened this period (spending patterns, major outliers, trends).
2) What risks or concerns you see.
3) 3–5 concrete, practical recommendations for the next 30–90 days.

Use plain language. Keep it under 400 words.
"""

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial planning assistant."},
                {"role": "user", "content": content},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error generating AI insights: {e}"
