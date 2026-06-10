"""
HDFC Bank PDF Statement Parser
Primary: pdfplumber text  |  Fallback: PyMuPDF  |  Bonus: pytesseract OCR

Supports HDFC formats:
  Format A: DD-Mon-YY  Narration  Ref  Amount  Balance   (no value date)
  Format B: DD/MM/YY   Narration  Ref  Withdrawal  Deposit  Balance
  Format C: pdfplumber table extraction
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from io import BytesIO

import pdfplumber

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class AccountInfo:
    holder_name: str = ""
    account_number: str = ""
    bank_name: str = "HDFC Bank"
    branch: str = ""
    ifsc: str = ""
    statement_from: str = ""
    statement_to: str = ""
    opening_balance: float = 0.0
    closing_balance: float = 0.0
    total_credit_count: int = 0
    total_credit_amount: float = 0.0
    total_debit_count: int = 0
    total_debit_amount: float = 0.0


@dataclass
class Transaction:
    date: str = ""
    value_date: str = ""
    description: str = ""
    cheque_ref: str = ""
    credit: Optional[float] = None
    debit: Optional[float] = None
    balance: float = 0.0
    category: str = "Other"


@dataclass
class ParseResult:
    account: AccountInfo = field(default_factory=AccountInfo)
    transactions: list = field(default_factory=list)
    parse_warnings: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Amount / date helpers
# ---------------------------------------------------------------------------

def _clean_amount(raw: str) -> Optional[float]:
    if not raw:
        return None
    cleaned = re.sub(r"[,\s]", "", raw.strip())
    cleaned = re.sub(r"(?i)(cr|dr)$", "", cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return None


# Matches:  01-Jun-24  /  01/06/2024  /  01/06/24  /  01-06-2024
DATE_PATTERN = re.compile(
    r"\b(\d{2}[/\-][A-Za-z]{3}[/\-]\d{2,4}|\d{2}[/\-]\d{2}[/\-]\d{4}|\d{2}[/\-]\d{2}[/\-]\d{2})\b"
)


def _is_date(val: str) -> bool:
    return bool(DATE_PATTERN.match(val.strip()))


def _normalize_date(raw: str) -> str:
    """Normalize all date variants to DD/MM/YYYY for consistency."""
    raw = raw.strip()
    # DD-Mon-YY → try to expand
    m = re.match(r"(\d{2})[/\-]([A-Za-z]{3})[/\-](\d{2,4})", raw)
    if m:
        day, mon_str, yr = m.groups()
        MONTHS = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        }
        mon = MONTHS.get(mon_str.lower(), mon_str)
        year = ("20" + yr) if len(yr) == 2 else yr
        return f"{day}/{mon}/{year}"
    # DD-MM-YYYY / DD/MM/YYYY / DD/MM/YY
    m2 = re.match(r"(\d{2})[/\-](\d{2})[/\-](\d{2,4})", raw)
    if m2:
        d, mo, y = m2.groups()
        year = ("20" + y) if len(y) == 2 else y
        return f"{d}/{mo}/{year}"
    return raw


def _parse_date_obj(date_str: str):
    from datetime import datetime
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

_ACCOUNT_NO_RE = re.compile(
    r"(?:Account\s*(?:No|Number|#|\.)\s*[:\-]?\s*)([0-9Xx ]{6,25})", re.IGNORECASE
)
_HOLDER_RE = re.compile(
    r"(?:Account\s*Holder\s*(?:Name)?\s*[:\-]?\s*|Customer\s*(?:Name)?\s*[:\-]?\s*)"
    r"([A-Z][A-Za-z\s\.]{3,60})",
    re.IGNORECASE,
)
_IFSC_RE = re.compile(r"\bIFSC\s*(?:Code)?\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})", re.IGNORECASE)
_BRANCH_RE = re.compile(
    r"(?:Branch\s*[:\-]?\s*)([A-Za-z0-9\s,\-\.]{3,60}?)(?:\n|IFSC|$)", re.IGNORECASE
)
_PERIOD_RE = re.compile(
    r"(?:Statement\s*Period\s*[:\-]?\s*)"
    r"(\d{2}[/\-][A-Za-z]{3}[/\-]\d{2,4}|\d{2}[/\-]\d{2}[/\-]\d{2,4})"
    r"(?:\s*(?:To|to|\-)\s*)"
    r"(\d{2}[/\-][A-Za-z]{3}[/\-]\d{2,4}|\d{2}[/\-]\d{2}[/\-]\d{2,4})",
    re.IGNORECASE,
)
_OB_RE = re.compile(r"Opening\s*Balance\s*[:\-]?\s*([\d,\.]+)", re.IGNORECASE)
_CB_RE = re.compile(r"Closing\s*Balance\s*[:\-]?\s*([\d,\.]+)", re.IGNORECASE)


def _extract_meta(full_text: str, info: AccountInfo) -> None:
    m = _ACCOUNT_NO_RE.search(full_text)
    if m:
        info.account_number = m.group(1).strip().replace(" ", "")

    m = _HOLDER_RE.search(full_text)
    if m:
        candidate = m.group(1).strip()
        # stop at newline
        candidate = candidate.split("\n")[0].strip()
        if len(candidate.split()) >= 2:
            info.holder_name = candidate

    m = _IFSC_RE.search(full_text)
    if m:
        info.ifsc = m.group(1).strip()

    m = _BRANCH_RE.search(full_text)
    if m:
        info.branch = m.group(1).strip()

    m = _PERIOD_RE.search(full_text)
    if m:
        info.statement_from = _normalize_date(m.group(1))
        info.statement_to = _normalize_date(m.group(2))

    m = _OB_RE.search(full_text)
    if m:
        v = _clean_amount(m.group(1))
        if v is not None:
            info.opening_balance = v

    m = _CB_RE.search(full_text)
    if m:
        v = _clean_amount(m.group(1))
        if v is not None:
            info.closing_balance = v


# ---------------------------------------------------------------------------
# FORMAT A  — DD-Mon-YY  Description  Ref  Amount  Balance
# (single amount col; CR/DR determined by balance direction)
# ---------------------------------------------------------------------------

# Matches a line that STARTS with a date and ENDS with two decimal amounts
FORMAT_A_RE = re.compile(
    r"^(\d{2}[/\-][A-Za-z]{3}[/\-]\d{2,4})"    # date
    r"\s+"
    r"(.+?)"                                       # description (lazy)
    r"\s+"
    r"([\d,]+\.\d{2})"                            # amount1
    r"\s+"
    r"([\d,]+\.\d{2})"                            # amount2 (balance)
    r"\s*$",
)

# Ref-number pattern inside description: trailing CAPS+digits token
_REF_TAIL_RE = re.compile(r"\s+([A-Z][A-Z0-9/\-]{4,20})\s*$")


def _parse_format_a(lines: list, opening_balance: float) -> list:
    """Parse Format A: date + desc + ref + single_amount + balance."""
    transactions = []
    prev_balance = opening_balance

    for line in lines:
        line = line.strip()
        m = FORMAT_A_RE.match(line)
        if not m:
            continue

        date_raw = m.group(1)
        desc_raw = m.group(2).strip()
        amt_raw = m.group(3)
        bal_raw = m.group(4)

        amount = _clean_amount(amt_raw)
        balance = _clean_amount(bal_raw)
        if amount is None or balance is None:
            continue

        # Extract ref from tail of description
        cheque_ref = ""
        ref_m = _REF_TAIL_RE.search(desc_raw)
        if ref_m:
            cheque_ref = ref_m.group(1)
            desc_raw = desc_raw[:ref_m.start()].strip()

        # Determine CR/DR from balance direction
        diff = round(balance - prev_balance, 2)
        credit = None
        debit = None

        if abs(diff - amount) <= 1.0:
            credit = amount
        elif abs(diff + amount) <= 1.0:
            debit = amount
        else:
            # Fallback: use balance direction
            if diff > 0:
                credit = amount
            else:
                debit = amount

        prev_balance = balance

        transactions.append(Transaction(
            date=_normalize_date(date_raw),
            value_date=_normalize_date(date_raw),
            description=re.sub(r"\s{2,}", " ", desc_raw),
            cheque_ref=cheque_ref,
            credit=credit,
            debit=debit,
            balance=balance,
        ))

    return transactions


# ---------------------------------------------------------------------------
# FORMAT B  — DD/MM/YY  ValueDate  Description  Ref  Withdrawal  Deposit  Balance
# (two separate amount columns)
# ---------------------------------------------------------------------------

FORMAT_B_RE = re.compile(
    r"^(\d{2}[/\-]\d{2}[/\-]\d{2,4})"           # date
    r"\s+"
    r"(\d{2}[/\-]\d{2}[/\-]\d{2,4})?"            # optional value date
    r"\s*"
    r"(.+?)"                                       # description
    r"\s{2,}"
    r"([A-Z0-9/\-]*)"                             # ref
    r"\s+"
    r"([\d,]+\.\d{2}|-)"                          # withdrawal OR deposit
    r"\s+"
    r"([\d,]+\.\d{2}|-)"                          # deposit OR withdrawal
    r"\s+"
    r"([\d,]+\.\d{2})"                            # closing balance
    r"\s*$",
    re.IGNORECASE,
)


def _parse_format_b(lines: list) -> list:
    transactions = []
    for line in lines:
        m = FORMAT_B_RE.match(line.strip())
        if not m:
            continue
        date = _normalize_date(m.group(1))
        vdate = _normalize_date(m.group(2)) if m.group(2) else date
        desc = re.sub(r"\s{2,}", " ", m.group(3)).strip()
        ref = m.group(4).strip()
        col5 = m.group(5).strip()
        col6 = m.group(6).strip()
        balance = _clean_amount(m.group(7)) or 0.0

        debit = _clean_amount(col5) if col5 != "-" else None
        credit = _clean_amount(col6) if col6 != "-" else None

        transactions.append(Transaction(
            date=date, value_date=vdate, description=desc,
            cheque_ref=ref, credit=credit, debit=debit, balance=balance,
        ))
    return transactions


# ---------------------------------------------------------------------------
# pdfplumber table extraction
# ---------------------------------------------------------------------------

HEADER_KEYWORDS = {"date", "narration", "withdrawal", "deposit", "balance", "chq", "value", "description"}


def _is_header_row(row: list) -> bool:
    text = " ".join(str(c or "").lower() for c in row)
    return sum(1 for k in HEADER_KEYWORDS if k in text) >= 2


def _row_has_date(row: list) -> bool:
    for cell in row:
        if cell and _is_date(str(cell)):
            return True
    return False


def _extract_from_table(table: list) -> list:
    transactions = []
    header_idx = None
    col_order = {}

    for i, row in enumerate(table):
        if _is_header_row(row):
            header_idx = i
            header = [str(c or "").lower() for c in row]
            for idx, h in enumerate(header):
                if "date" in h and "value" not in h:
                    col_order.setdefault("date", idx)
                elif "value" in h:
                    col_order["value_date"] = idx
                elif "narration" in h or "description" in h or "particular" in h:
                    col_order["desc"] = idx
                elif "chq" in h or "ref" in h or "cheque" in h:
                    col_order["ref"] = idx
                elif "withdrawal" in h or "debit" in h or " dr" in h:
                    col_order["debit"] = idx
                elif "deposit" in h or "credit" in h or " cr" in h:
                    col_order["credit"] = idx
                elif "balance" in h or "closing" in h:
                    col_order["balance"] = idx
            break

    start = (header_idx + 1) if header_idx is not None else 0

    for row in table[start:]:
        if not _row_has_date(row):
            continue
        cells = [str(c or "").strip() for c in row]
        if len(cells) < 4:
            continue
        try:
            d_idx = col_order.get("date", 0)
            vd_idx = col_order.get("value_date", d_idx)
            desc_idx = col_order.get("desc", 2)
            ref_idx = col_order.get("ref", 3)
            dr_idx = col_order.get("debit")
            cr_idx = col_order.get("credit")
            bal_idx = col_order.get("balance", len(cells) - 1)

            date = _normalize_date(cells[d_idx])
            vdate = _normalize_date(cells[vd_idx])
            desc = re.sub(r"\s{2,}", " ", cells[desc_idx]).strip()
            ref = cells[ref_idx] if ref_idx < len(cells) else ""
            debit = _clean_amount(cells[dr_idx]) if dr_idx is not None and dr_idx < len(cells) else None
            credit = _clean_amount(cells[cr_idx]) if cr_idx is not None and cr_idx < len(cells) else None
            balance = _clean_amount(cells[bal_idx]) or 0.0

            transactions.append(Transaction(
                date=date, value_date=vdate, description=desc,
                cheque_ref=ref, credit=credit, debit=debit, balance=balance,
            ))
        except Exception as exc:
            logger.debug("Table row error: %s — %s", cells, exc)

    return transactions


# ---------------------------------------------------------------------------
# OCR / PyMuPDF fallbacks
# ---------------------------------------------------------------------------

def _extract_with_pymupdf(pdf_bytes: bytes) -> list:
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        lines = []
        for page in doc:
            lines.extend(page.get_text("text").splitlines())
        return lines
    except Exception as exc:
        logger.warning("PyMuPDF fallback failed: %s", exc)
        return []


def _extract_with_ocr(pdf_bytes: bytes) -> list:
    try:
        import fitz
        import pytesseract
        from PIL import Image
        import io
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        lines = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, config="--psm 6")
            lines.extend(text.splitlines())
        return lines
    except Exception as exc:
        logger.warning("OCR fallback failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Balance-chain validation
# ---------------------------------------------------------------------------

def _validate_balance_chain(transactions: list, warnings: list) -> None:
    for i in range(1, len(transactions)):
        prev = transactions[i - 1]
        curr = transactions[i]
        expected = prev.balance
        if curr.credit:
            expected += curr.credit
        elif curr.debit:
            expected -= curr.debit
        if abs(expected - curr.balance) > 2.0:
            warnings.append(
                f"Balance chain mismatch at row {i + 1}: "
                f"expected {expected:.2f}, got {curr.balance:.2f}"
            )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_hdfc_statement(pdf_bytes: bytes) -> ParseResult:
    result = ParseResult()
    full_text_parts = []
    transactions = []

    # ── Step 1: extract all text via pdfplumber ────────────────────────────
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text_parts.append(text)

                # Try table extraction first
                for table in (page.extract_tables() or []):
                    if table:
                        txns = _extract_from_table(table)
                        transactions.extend(txns)
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)

    full_text = "\n".join(full_text_parts)
    all_lines = full_text.splitlines()

    logger.info("pdfplumber table extraction: %d transactions", len(transactions))

    # ── Step 2: try Format B (two-column amount) line regex ────────────────
    if len(transactions) < 3:
        fmt_b = _parse_format_b(all_lines)
        logger.info("Format B line parse: %d transactions", len(fmt_b))
        if len(fmt_b) > len(transactions):
            transactions = fmt_b

    # ── Step 3: try Format A (single amount col, balance-direction CR/DR) ──
    if len(transactions) < 3:
        # need opening balance for direction logic
        ob_m = _OB_RE.search(full_text)
        ob = _clean_amount(ob_m.group(1)) if ob_m else 0.0
        fmt_a = _parse_format_a(all_lines, ob or 0.0)
        logger.info("Format A line parse: %d transactions", len(fmt_a))
        if len(fmt_a) > len(transactions):
            transactions = fmt_a

    # ── Step 4: PyMuPDF fallback ───────────────────────────────────────────
    if len(transactions) < 3:
        mu_lines = _extract_with_pymupdf(pdf_bytes)
        if mu_lines:
            ob_m = _OB_RE.search("\n".join(mu_lines))
            ob = _clean_amount(ob_m.group(1)) if ob_m else 0.0
            fmt_a = _parse_format_a(mu_lines, ob or 0.0)
            if len(fmt_a) > len(transactions):
                transactions = fmt_a
                full_text = full_text or "\n".join(mu_lines)

    # ── Step 5: OCR ────────────────────────────────────────────────────────
    if len(transactions) < 3:
        ocr_lines = _extract_with_ocr(pdf_bytes)
        if ocr_lines:
            ob_m = _OB_RE.search("\n".join(ocr_lines))
            ob = _clean_amount(ob_m.group(1)) if ob_m else 0.0
            fmt_a = _parse_format_a(ocr_lines, ob or 0.0)
            if len(fmt_a) > len(transactions):
                transactions = fmt_a

    if len(transactions) < 2:
        result.parse_warnings.append(
            "Very few transactions extracted — PDF may use an unsupported format."
        )

    # ── Extract account metadata ───────────────────────────────────────────
    _extract_meta(full_text, result.account)

    # ── Deduplicate ────────────────────────────────────────────────────────
    seen = set()
    unique = []
    for t in transactions:
        key = (t.date, t.description[:40], t.balance)
        if key not in seen:
            seen.add(key)
            unique.append(t)
    transactions = unique

    # ── Sort chronologically ───────────────────────────────────────────────
    transactions.sort(key=lambda t: _parse_date_obj(t.date) or t.date)

    # ── Compute totals ─────────────────────────────────────────────────────
    credits = [t for t in transactions if t.credit]
    debits = [t for t in transactions if t.debit]
    result.account.total_credit_count = len(credits)
    result.account.total_credit_amount = round(sum(t.credit for t in credits), 2)
    result.account.total_debit_count = len(debits)
    result.account.total_debit_amount = round(sum(t.debit for t in debits), 2)

    if transactions and result.account.opening_balance == 0.0:
        first = transactions[0]
        if first.credit:
            result.account.opening_balance = round(first.balance - first.credit, 2)
        elif first.debit:
            result.account.opening_balance = round(first.balance + first.debit, 2)

    if transactions and result.account.closing_balance == 0.0:
        result.account.closing_balance = transactions[-1].balance

    # ── Validate balance chain ─────────────────────────────────────────────
    _validate_balance_chain(transactions, result.parse_warnings)

    result.transactions = transactions
    return result
