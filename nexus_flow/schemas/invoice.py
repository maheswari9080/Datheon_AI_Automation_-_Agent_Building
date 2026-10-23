"""Pydantic schemas for Invoice Intelligence Engine."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LineItemCreate(BaseModel):
    description: str
    quantity: float = Field(default=1.0, ge=0.0)
    unit_price: float = Field(default=0.0, ge=0.0)
    line_total: float = Field(default=0.0, ge=0.0)

class ExtractedInvoiceData(BaseModel):
    vendor: Optional[str] = "Unknown Vendor"
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: str = "USD"
    line_items: List[LineItemCreate] = Field(default_factory=list)
    subtotal: float = 0.0
    discount: float = 0.0
    tax_amount: float = 0.0
    extracted_total: float = 0.0
    payment_status: Optional[str] = "UNPAID"

class ArithmeticValidationResult(BaseModel):
    is_valid: bool
    calculated_total: float
    extracted_total: float
    variance: float
    discrepancy_notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: str
    subtotal: float
    discount: float
    tax_amount: float
    calculated_total: float
    extracted_total: float
    is_arithmetic_valid: bool
    discrepancy_notes: Optional[str] = None
    duplicate_flag: bool
    status: str
    payment_status: str
    google_sheets_row: Optional[int] = None
    line_items: List[LineItemCreate] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class SheetsExportPayload(BaseModel):
    invoice_id: str
    spreadsheet_id: Optional[str] = None
