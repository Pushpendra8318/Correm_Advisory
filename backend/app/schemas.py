from pydantic import BaseModel
from typing import Optional


class TransactionOut(BaseModel):
    date: str
    value_date: str
    description: str
    cheque_ref: str
    credit: Optional[float]
    debit: Optional[float]
    balance: float
    category: str


class AccountInfoOut(BaseModel):
    holder_name: str
    account_number: str
    bank_name: str
    branch: str
    ifsc: str
    statement_from: str
    statement_to: str
    opening_balance: float
    closing_balance: float
    total_credit_count: int
    total_credit_amount: float
    total_debit_count: int
    total_debit_amount: float


class CategorySummaryItem(BaseModel):
    category: str
    total_credit: float
    total_debit: float
    count: int


class UploadResponse(BaseModel):
    session_id: str
    account: AccountInfoOut
    transactions: list[TransactionOut]
    category_summary: list[CategorySummaryItem]
    parse_warnings: list[str]
    total_transactions: int
    pct_categorized: float
