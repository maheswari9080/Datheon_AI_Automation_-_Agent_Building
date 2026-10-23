"""API routes for Invoice Intelligence Engine."""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from nexus_flow.db.session import get_db
from nexus_flow.engines.invoice.service import InvoiceEngine
from nexus_flow.schemas.common import ApiResponse

router = APIRouter(prefix="/invoices", tags=["Invoice Intelligence"])

def get_invoice_engine(db: Session = Depends(get_db)) -> InvoiceEngine:
    return InvoiceEngine(db=db)

@router.post("/upload", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...), engine: InvoiceEngine = Depends(get_invoice_engine)
):
    try:
        content = await file.read()
        res = engine.process_invoice(filename=file.filename or "invoice.pdf", content=content)
        return ApiResponse(
            success=True,
            message="Invoice processed and audited successfully",
            data={
                "invoice_id": res["invoice_id"],
                "filename": res["filename"],
                "vendor": res["vendor"],
                "invoice_number": res["invoice_number"],
                "extracted_total": res["extracted_total"],
                "calculated_total": res["calculated_total"],
                "is_arithmetic_valid": res["is_arithmetic_valid"],
                "duplicate_flag": res["duplicate_flag"],
                "status": res["status"],
                "line_items_count": res["line_items_count"],
            },
            execution_time_ms=res["duration_ms"],
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ApiResponse[List[dict]])
def list_invoices(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    engine: InvoiceEngine = Depends(get_invoice_engine),
):
    invoices = engine.list_invoices(status=status_filter, limit=limit)
    out = []
    for inv in invoices:
        items = [
            {
                "description": it.description,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "line_total": it.line_total,
            }
            for it in inv.line_items
        ]
        out.append({
            "id": inv.id,
            "filename": inv.filename,
            "vendor": inv.vendor,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "currency": inv.currency,
            "subtotal": inv.subtotal,
            "discount": inv.discount,
            "tax_amount": inv.tax_amount,
            "extracted_total": inv.extracted_total,
            "calculated_total": inv.calculated_total,
            "is_arithmetic_valid": inv.is_arithmetic_valid,
            "discrepancy_notes": inv.discrepancy_notes,
            "duplicate_flag": inv.duplicate_flag,
            "status": inv.status,
            "payment_status": inv.payment_status,
            "google_sheets_row": inv.google_sheets_row,
            "line_items": items,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        })
    return ApiResponse(success=True, data=out)

@router.get("/{invoice_id}", response_model=ApiResponse[dict])
def get_invoice(invoice_id: str, engine: InvoiceEngine = Depends(get_invoice_engine)):
    inv = engine.get_invoice(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    items = [
        {
            "description": it.description,
            "quantity": it.quantity,
            "unit_price": it.unit_price,
            "line_total": it.line_total,
        }
        for it in inv.line_items
    ]
    return ApiResponse(
        success=True,
        data={
            "id": inv.id,
            "filename": inv.filename,
            "vendor": inv.vendor,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "currency": inv.currency,
            "extracted_total": inv.extracted_total,
            "calculated_total": inv.calculated_total,
            "is_arithmetic_valid": inv.is_arithmetic_valid,
            "discrepancy_notes": inv.discrepancy_notes,
            "duplicate_flag": inv.duplicate_flag,
            "status": inv.status,
            "google_sheets_row": inv.google_sheets_row,
            "line_items": items,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        },
    )

@router.post("/{invoice_id}/approve", response_model=ApiResponse[dict])
def approve_invoice(invoice_id: str, engine: InvoiceEngine = Depends(get_invoice_engine)):
    try:
        res = engine.approve_invoice(invoice_id=invoice_id)
        return ApiResponse(success=True, message="Invoice approved successfully", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.post("/{invoice_id}/export", response_model=ApiResponse[dict])
def export_invoice(invoice_id: str, engine: InvoiceEngine = Depends(get_invoice_engine)):
    try:
        res = engine.export_to_sheets(invoice_id=invoice_id)
        return ApiResponse(success=True, message="Invoice exported to Google Sheets", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
