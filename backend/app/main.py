"""
FastAPI entry point for HDFC Bank Statement Analyzer.
Routes:
  POST /upload    — parse PDF, return JSON summary + session_id
  GET  /download/{session_id} — return .xlsx file
  GET  /health    — health check
"""

import json
import logging
import uuid
from collections import defaultdict
from dataclasses import asdict

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.categorizer import categorize_all, get_categorization_stats
from app.excel_generator import generate_excel
from app.models import AnalysisSession, get_db, init_db
from app.parser import AccountInfo, Transaction, parse_hdfc_statement
from app.schemas import (
    AccountInfoOut,
    CategorySummaryItem,
    TransactionOut,
    UploadResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HDFC Bank Statement Analyzer",
    description="Upload an HDFC Bank PDF statement and download a structured Excel report.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized")


@app.get("/health")
def health():
    return {"status": "ok", "service": "HDFC Statement Analyzer"}


@app.post("/debug-pdf")
async def debug_pdf(file: UploadFile = File(...)):
    """Returns raw extracted text and table data — use to diagnose parse failures."""
    pdf_bytes = await file.read()
    import pdfplumber
    from io import BytesIO

    result = {"pages": [], "raw_lines": []}
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                tables = page.extract_tables() or []
                result["pages"].append({
                    "page": i + 1,
                    "text_preview": text[:2000],
                    "tables": [t[:5] for t in tables],  # first 5 rows of each table
                    "num_tables": len(tables),
                })
                result["raw_lines"].extend(text.splitlines()[:50])
    except Exception as e:
        result["error"] = str(e)
    return result


@app.post("/upload", response_model=UploadResponse)
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="Uploaded file appears to be empty or corrupt.")

    logger.info("Parsing PDF: %s (%d bytes)", file.filename, len(pdf_bytes))

    try:
        result = parse_hdfc_statement(pdf_bytes)
    except Exception as exc:
        logger.exception("PDF parsing failed")
        raise HTTPException(status_code=422, detail=f"Failed to parse PDF: {str(exc)}")

    transactions = result.transactions
    account = result.account

    if not transactions:
        raise HTTPException(
            status_code=422,
            detail="No transactions could be extracted from this PDF. "
                   "Please ensure it is a valid HDFC Bank statement.",
        )

    # Categorize
    categorize_all(transactions)

    # Build category summary
    cat_data: dict[str, dict] = defaultdict(lambda: {"credit": 0.0, "debit": 0.0, "count": 0})
    for txn in transactions:
        cat_data[txn.category]["count"] += 1
        if txn.credit:
            cat_data[txn.category]["credit"] += txn.credit
        if txn.debit:
            cat_data[txn.category]["debit"] += txn.debit

    category_summary = [
        CategorySummaryItem(
            category=cat,
            total_credit=round(data["credit"], 2),
            total_debit=round(data["debit"], 2),
            count=data["count"],
        )
        for cat, data in sorted(cat_data.items())
    ]

    stats = get_categorization_stats(transactions)

    # Persist session
    session_id = str(uuid.uuid4())
    session_obj = AnalysisSession(
        session_id=session_id,
        account_json=json.dumps(asdict(account)),
        transactions_json=json.dumps([asdict(t) for t in transactions]),
    )
    db.add(session_obj)
    db.commit()

    return UploadResponse(
        session_id=session_id,
        account=AccountInfoOut(**asdict(account)),
        transactions=[TransactionOut(**asdict(t)) for t in transactions[:200]],
        category_summary=category_summary,
        parse_warnings=result.parse_warnings,
        total_transactions=len(transactions),
        pct_categorized=stats["pct_categorized"],
    )


@app.get("/download/{session_id}")
def download_excel(session_id: str, db: Session = Depends(get_db)):
    session_obj = db.query(AnalysisSession).filter_by(session_id=session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found. Please upload again.")

    account_dict = json.loads(session_obj.account_json)
    txn_list = json.loads(session_obj.transactions_json)

    account = AccountInfo(**account_dict)
    transactions = [Transaction(**t) for t in txn_list]

    try:
        excel_bytes = generate_excel(account, transactions)
    except Exception as exc:
        logger.exception("Excel generation failed")
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(exc)}")

    filename = f"HDFC_Statement_{account.account_number or session_id[:8]}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
