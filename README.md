# StatementIQ — HDFC Bank Statement Analyzer

> Full-stack web application to parse HDFC Bank PDF statements, categorize every transaction, and export a structured 3-sheet Excel report.

## Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | `https://your-app.vercel.app` _(update after Vercel deploy)_ |
| **Backend** | `https://correm-advisory.onrender.com` |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | ReactJS 18, Vite 5, Tailwind CSS 3 |
| Backend | Python 3.11, FastAPI, Uvicorn |
| PDF Parsing | pdfplumber (primary), PyMuPDF / fitz (fallback), pytesseract (OCR bonus) |
| Excel Output | openpyxl |
| Database | SQLite via SQLAlchemy (session-based storage) |
| Charts | Recharts |
| Deployment | Vercel (frontend) + Render (backend via Docker) |

---

## Architecture

```
┌─────────────┐    POST /upload     ┌──────────────────────────────────────┐
│  React SPA  │ ─────────────────► │  FastAPI Backend                     │
│  (Vercel)   │                     │                                      │
│             │ ◄─ JSON summary ─── │  1. parser.py                        │
│  - Upload   │                     │     pdfplumber tables → raw rows     │
│  - Dashboard│    GET /download    │     PyMuPDF fallback if < 5 rows     │
│  - Table    │ ─────────────────► │     pytesseract OCR for scanned PDFs │
│  - Charts   │ ◄─ .xlsx file ───── │                                      │
│  - Download │                     │  2. categorizer.py                   │
└─────────────┘                     │     15 categories, 200+ keywords     │
                                    │     regex/substring matching          │
                                    │                                      │
                                    │  3. excel_generator.py               │
                                    │     Sheet 1: Account Details         │
                                    │     Sheet 2: Transaction Ledger      │
                                    │     Sheet 3: Category Analytics      │
                                    │                                      │
                                    │  4. SQLite session storage           │
                                    │     session_id links upload→download │
                                    └──────────────────────────────────────┘
```

### Parsing Pipeline

1. **pdfplumber table extraction** — HDFC PDFs with embedded tables are parsed directly using `extract_tables()`. Column headers are auto-detected (Date, Value Date, Narration, Chq/Ref No, Withdrawal, Deposit, Closing Balance).

2. **Regex line-by-line fallback** — If table extraction yields < 5 rows, the full page text is scanned line-by-line with a regex pattern that matches HDFC's standard transaction row format.

3. **PyMuPDF fallback** — If pdfplumber text extraction fails (e.g. malformed PDF structure), PyMuPDF's `get_text()` is used to extract raw text, then regex-parsed.

4. **OCR for scanned PDFs (bonus)** — If all text extraction yields < 5 rows, pages are rendered to 200 DPI images and OCR'd via pytesseract. Requires Tesseract installed.

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Tesseract OCR for scanned PDF support

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local and set VITE_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Deployment

### Backend (Render)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set root directory to `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Or use the included `Dockerfile` for Docker-based deploy

### Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. Set root directory to `frontend`
4. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`
5. Deploy

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload HDFC PDF, returns JSON with session_id |
| `GET` | `/download/{session_id}` | Download 3-sheet Excel file |

### POST /upload Response

```json
{
  "session_id": "uuid",
  "account": {
    "holder_name": "JOHN DOE",
    "account_number": "XXXX1234",
    "bank_name": "HDFC Bank",
    "branch": "Mumbai Main Branch",
    "ifsc": "HDFC0001234",
    "statement_from": "01/04/2024",
    "statement_to": "31/03/2025",
    "opening_balance": 10000.00,
    "closing_balance": 25000.00,
    "total_credit_count": 12,
    "total_credit_amount": 120000.00,
    "total_debit_count": 85,
    "total_debit_amount": 105000.00
  },
  "transactions": [...],
  "category_summary": [...],
  "parse_warnings": [],
  "total_transactions": 97,
  "pct_categorized": 92.8
}
```

---

## Excel Output

| Sheet | Contents |
|-------|----------|
| **Account Details** | Account holder info, balances, credit/debit totals |
| **Transaction Ledger** | All transactions, color-coded (green=credit, red=debit), with category |
| **Analytics** | Category summary, month-wise breakdown, top 5 transactions, salary detection, EMI detection, categorization % |

---

## Categories & Keywords

15 categories with 200+ keywords total:

| Category | Sample Keywords |
|----------|----------------|
| Salary | SALARY, PAYROLL, STIPEND, WAGES, NEFT CR SALARY, +12 more |
| EMI / Loan | EMI, LOAN, NACH DR, ECS DR, INSTALLMENT, HOME LOAN, +18 more |
| Food & Dining | SWIGGY, ZOMATO, BLINKIT, ZEPTO, PIZZA, BURGER, +18 more |
| Travel | IRCTC, UBER, OLA, PETROL, INDIGO, FASTAG, +22 more |
| Shopping | AMAZON, FLIPKART, MYNTRA, BIGBASKET, CROMA, +16 more |
| Utilities | ELECTRICITY, BESCOM, BBPS, TATA POWER, LPG, +20 more |
| Telecom | AIRTEL, JIO, VODAFONE, BSNL, BROADBAND, DTH, +14 more |
| Entertainment | NETFLIX, HOTSTAR, SPOTIFY, PVR, INOX, STEAM, +14 more |
| Healthcare | PHARMACY, APOLLO, MEDPLUS, 1MG, HOSPITAL, +18 more |
| Education | UDEMY, COURSERA, BYJU, SCHOOL FEE, COACHING, +14 more |
| Investments | MUTUAL FUND, SIP, ZERODHA, GROWW, NSE, BSE, +16 more |
| Insurance | LIC, HDFC LIFE, PREMIUM, BAJAJ ALLIANZ, +16 more |
| Cash Withdrawal | ATM, CASH WDL, CDM, ATM WITHDRAWAL, +4 more |
| UPI / Transfer | UPI, BHIM, PHONEPE, GPAY, NEFT, IMPS, RTGS, +10 more |
| Rent | RENT, LEASE, PG, LANDLORD, SOCIETY, +10 more |

---

## Assumptions Made

1. **HDFC statement format**: The parser is tuned for HDFC Bank's standard PDF format (text-based). Columns assumed: Date | Value Date | Narration | Chq/Ref No | Withdrawal Amt | Deposit Amt | Closing Balance.

2. **Date formats**: Supports `DD/MM/YYYY` and `DD/MM/YY` formats as used in HDFC statements.

3. **Balance chain validation**: Uses ±₹1.00 tolerance for floating point rounding differences in the PDF.

4. **Salary detection**: Identifies transactions with the largest monthly credit per calendar month, checks if amounts are within ±15% of each other across ≥2 months.

5. **EMI detection**: Groups recurring debits by rounded amount (nearest ₹100), marks as EMI if same approximate amount appears across ≥2 calendar months.

6. **Session storage**: Session data is persisted in SQLite for the download. In production on Render, data persists until the instance restarts (ephemeral storage).

7. **Password-protected PDFs**: Not supported — HDFC statements downloaded from NetBanking are typically unprotected.

---

## AI Tools Disclosure

| Tool | Usage |
|------|-------|
| **Claude (Anthropic Claude Sonnet)** | Scaffolded the full architecture, wrote the PDF parsing logic (regex patterns for HDFC format), categorization keyword list (200+ keywords), openpyxl Excel formatting code (styles, colors, auto-fit), React components, and helped debug edge cases |

All code was reviewed and integrated by the candidate. The business logic, architectural decisions, and integration between components were understood and verified end-to-end.

---

## Project Structure

```
hdfc-analyzer/
├── frontend/                  # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadCard.jsx         # Drag-drop PDF upload
│   │   │   ├── SummaryDashboard.jsx   # Account overview cards
│   │   │   ├── TransactionTable.jsx   # Searchable, sortable table
│   │   │   ├── CategoryChart.jsx      # Pie + bar chart
│   │   │   └── DownloadButton.jsx     # Excel download CTA
│   │   ├── utils/
│   │   │   ├── api.js                 # Axios API client
│   │   │   └── format.js             # Currency/category formatters
│   │   ├── App.jsx                    # Main application shell
│   │   └── index.css                 # Tailwind + custom styles
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI routes + CORS
│   │   ├── parser.py                 # PDF extraction (4 strategies)
│   │   ├── categorizer.py            # 15 categories, 200+ keywords
│   │   ├── excel_generator.py        # 3-sheet openpyxl builder
│   │   ├── models.py                 # SQLAlchemy session model
│   │   └── schemas.py               # Pydantic request/response schemas
│   ├── requirements.txt
│   └── Dockerfile
│
└── README.md
```
