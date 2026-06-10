"""
Generates a realistic HDFC Bank statement test PDF.
Run: python generate_test_pdf.py
Output: hdfc_test_statement.pdf
"""

from fpdf import FPDF

TRANSACTIONS = [
    ("01-Jun-24", "NEFT CR SALARY TECHCORP PVT LTD",    "REF001234", "55000.00", "",       "100230.00"),
    ("02-Jun-24", "UPI/SWIGGY FOOD ORDER/9876543210",   "UPI002345", "",         "450.00",  "99780.00"),
    ("03-Jun-24", "UPI/AMAZON PAY/ORDER98765",           "UPI003456", "",         "1299.00", "98481.00"),
    ("04-Jun-24", "NACH DR HDFC LOAN EMI JUNE",          "NACH00456", "",         "8500.00", "89981.00"),
    ("05-Jun-24", "UPI/PHONEPE/RENT PAYMENT",            "UPI005678", "",         "12000.00","77981.00"),
    ("06-Jun-24", "UPI/ZOMATO/ORDER123456",              "UPI006789", "",         "320.00",  "77661.00"),
    ("07-Jun-24", "ATM WDL HDFC ATM CP DELHI",           "ATM007890", "",         "5000.00", "72661.00"),
    ("08-Jun-24", "UPI/AIRTEL POSTPAID BILL",            "UPI008901", "",         "799.00",  "71862.00"),
    ("09-Jun-24", "UPI/NETFLIX SUBSCRIPTION",            "UPI009012", "",         "649.00",  "71213.00"),
    ("10-Jun-24", "UPI/UBER RIDE/9876543210",            "UPI010123", "",         "180.00",  "71033.00"),
    ("11-Jun-24", "UPI/FLIPKART/ORDER456789",            "UPI011234", "",         "2499.00", "68534.00"),
    ("12-Jun-24", "UPI/IRCTC TICKET BOOKING",            "UPI012345", "",         "1200.00", "67334.00"),
    ("13-Jun-24", "UPI/APOLLO PHARMACY",                 "UPI013456", "",         "870.00",  "66464.00"),
    ("14-Jun-24", "UPI/GROWW SIP MUTUAL FUND",           "UPI014567", "",         "5000.00", "61464.00"),
    ("15-Jun-24", "NACH DR HDFC LOAN EMI 2",             "NACH01456", "",         "6500.00", "54964.00"),
    ("16-Jun-24", "UPI/BESCOM ELECTRICITY BILL",         "UPI016789", "",         "1200.00", "53764.00"),
    ("17-Jun-24", "UPI/JIO RECHARGE/9876543210",         "UPI017890", "",         "239.00",  "53525.00"),
    ("18-Jun-24", "UPI/UDEMY COURSE PURCHASE",           "UPI018901", "",         "1299.00", "52226.00"),
    ("19-Jun-24", "UPI/ZERODHA TRADING ACCOUNT",         "UPI019012", "",         "2000.00", "50226.00"),
    ("20-Jun-24", "LIC PREMIUM DEBIT",                   "LIC020123", "",         "3500.00", "46726.00"),
    ("21-Jun-24", "NEFT/RECEIVED FROM PARENTS",          "NEFT02123", "8000.00",  "",        "54726.00"),
    ("22-Jun-24", "UPI/MYNTRA FASHION ORDER",            "UPI022345", "",         "1499.00", "53227.00"),
    ("23-Jun-24", "UPI/HOTSTAR SUBSCRIPTION",            "UPI023456", "",         "299.00",  "52928.00"),
    ("24-Jun-24", "UPI/MEDPLUS PHARMACY",                "UPI024567", "",         "200.00",  "52728.00"),
    ("25-Jun-24", "UPI/OLA RIDE/9876543210",             "UPI025678", "",         "155.00",  "52573.00"),
    ("26-Jun-24", "UPI/RAPIDO BIKE RIDE",                "UPI026789", "",         "80.00",   "52493.00"),
    ("27-Jun-24", "UPI/COURSERA SUBSCRIPTION",           "UPI027890", "",         "497.50",  "51995.50"),
    ("28-Jun-24", "UPI/SPOTIFY PREMIUM",                 "UPI028901", "",         "119.00",  "51876.50"),
    ("29-Jun-24", "NACH DR HDFC LOAN EMI 3",             "NACH02890", "",         "8400.00", "43476.50"),
    ("30-Jun-24", "INTEREST CREDIT HDFC SAVINGS",        "INT030124", "350.00",   "",        "43826.50"),
    ("30-Jun-24", "CHARGES DEBIT GST ON FEES",           "CHG030125", "",         "296.50",  "43530.00"),
    ("30-Jun-24", "IMPS CR FROM FREELANCE CLIENT",       "IMPS03012", "1500.00",  "",        "45030.00"),
]


class HDFCPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(128)
        self.cell(0, 5, "This is a computer generated statement. HDFC Bank Limited.", align="C")


def generate():
    pdf = HDFCPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(10, 10, 10)

    # ── Bank Header ──────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 51, 153)
    pdf.cell(0, 8, "HDFC BANK LIMITED", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, "Branch: Connaught Place, New Delhi", ln=True, align="C")
    pdf.cell(0, 5, "IFSC Code: HDFC0001234    Customer Care: 1800-202-6161", ln=True, align="C")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, "ACCOUNT STATEMENT", ln=True, align="C")
    pdf.ln(3)

    # ── Account Details ───────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "", 9)
    details = [
        ("Account Holder Name", "Akash Kumar Sharma"),
        ("Account Number", "5020 1234 5678 9012"),
        ("Account Type", "Savings Account"),
        ("Branch", "Connaught Place, New Delhi"),
        ("IFSC Code", "HDFC0001234"),
        ("Statement Period", "01-Jun-2024 To 30-Jun-2024"),
        ("Opening Balance", "45,230.00"),
        ("Closing Balance", "43,530.00"),
    ]
    for label, value in details:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(60, 5, f"{label} :", ln=False)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, value, ln=True)
    pdf.ln(4)

    # ── Divider ───────────────────────────────────────────────────────────────
    pdf.set_draw_color(0, 51, 153)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 287, pdf.get_y())
    pdf.ln(2)

    # ── Table Header ─────────────────────────────────────────────────────────
    pdf.set_fill_color(0, 51, 153)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    col_widths = [22, 90, 30, 28, 28, 30]
    headers = ["Date", "Narration", "Chq/Ref No", "Deposit", "Withdrawal", "Balance"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 6, h, border=1, align="C", fill=True)
    pdf.ln()

    # ── Transactions ─────────────────────────────────────────────────────────
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    fill = False
    for i, (date, narr, ref, dep, wdl, bal) in enumerate(TRANSACTIONS):
        bg = (240, 248, 255) if fill else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.cell(col_widths[0], 5.5, date, border=1, align="C", fill=True)
        pdf.cell(col_widths[1], 5.5, narr[:48], border=1, fill=True)
        pdf.cell(col_widths[2], 5.5, ref, border=1, align="C", fill=True)
        pdf.cell(col_widths[3], 5.5, dep, border=1, align="R", fill=True)
        pdf.cell(col_widths[4], 5.5, wdl, border=1, align="R", fill=True)
        pdf.cell(col_widths[5], 5.5, bal, border=1, align="R", fill=True)
        pdf.ln()
        fill = not fill

    # ── Summary ───────────────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_draw_color(0, 51, 153)
    pdf.line(10, pdf.get_y(), 287, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "SUMMARY", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Total Credits  :  4 transactions    Amount: 64,850.00", ln=True)
    pdf.cell(0, 5, "Total Debits   :  28 transactions   Amount: 64,550.00", ln=True)
    pdf.cell(0, 5, "Closing Balance:  43,530.00", ln=True)

    out_path = "hdfc_test_statement.pdf"
    pdf.output(out_path)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    generate()
