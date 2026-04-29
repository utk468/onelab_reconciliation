from pydantic import BaseModel, Field
from typing import Optional, List

class TransactionSchema(BaseModel):
    txn_id: str
    amount: float
    date: str
    type: str

class SettlementSchema(BaseModel):
    txn_id: str
    settled_amount: float
    settlement_date: str

class IssueSchema(BaseModel):
    txn_id: str
    issue_type: str
    description: str
    platform_amount: Optional[float] = None
    bank_amount: Optional[float] = None
    explanation: Optional[str] = None

class ReconciliationReportSchema(BaseModel):
    report_id: str
    generated_at: str
    total_transactions: int
    total_settlements: int
    total_mismatch_amount: float
    issues_count: int
    issues: List[IssueSchema]
