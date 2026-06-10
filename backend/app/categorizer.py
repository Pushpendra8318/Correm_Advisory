"""
Transaction Categorization Engine — keyword/regex based.
Covers 15 named categories + Other fallback.
"""

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Category keyword map  (uppercase, substring-matched)
# ---------------------------------------------------------------------------

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    (
        "Salary",
        [
            "SALARY", "SAL CREDIT", "SAL/", "/SAL", "PAYROLL", "STIPEND", "WAGES",
            "NEFT CR SALARY", "MONTHLY PAY", "EMPLOYER", "SALARY CREDIT", "PAY CREDIT",
            "REMUNERATION", "CTGRAT", "BONUS CREDIT", "INCENTIVE CREDIT", "ARREAR",
            "PAYSLIP", "COMPENSATION", "GROSS PAY", "NET PAY", "TAKE HOME",
            "HR PAYROLL", "PAYROLL CREDIT", "EMPLOYER NEFT", "STAFF PAY",
            "SALARY TRANSFER", "MONTHLY SALARY", "MONTHLY WAGES", "ANNUAL BONUS",
        ],
    ),
    (
        "EMI / Loan",
        [
            "EMI", "LOAN", "HDFC LOAN", "BAJAJ FIN", "NACH DR", "ECS DR", "REPAY",
            "INSTALLMENT", "EQUATED", "AUTO DEBIT EMI", "KOTAK LOAN", "AXIS EMI",
            "ICICI EMI", "SBI LOAN", "CREDIT CARD DUE", "CARD REPAYMENT", "INTEREST",
            "HOME LOAN", "CAR LOAN", "PERSONAL LOAN", "VEHICLE LOAN", "GOLD LOAN",
            "EDUCATION LOAN", "BUSINESS LOAN", "TATA CAPITAL", "FULLERTON",
            "MUTHOOT", "L&T FINANCE", "PIRAMAL", "ADITYA BIRLA FIN",
            "HDFC CRED", "ICICILOAN", "HDBFS", "HERO FINCORP",
            "LOAN REPAYMENT", "EMI DEBIT", "NACH DEBIT", "ECS PAYMENT",
            "HOME FINANCE", "MORTGAGE", "DEBENTURE INT", "LOAN INTEREST",
        ],
    ),
    (
        "Food & Dining",
        [
            "SWIGGY", "ZOMATO", "RESTAURANT", "CAFE", "DOMINOS", "MCDONALD",
            "BLINKIT", "ZEPTO", "DUNZO", "INSTAMART", "STARBUCKS", "HALDIRAM",
            "BBQ", "DINE", "PIZZA", "BURGER", "BIRYANI", "FOOD", "KITCHEN",
            "HOTEL", "BAKERY", "EATERY", "DHABA", "CANTEEN", "MESS",
            "BURGER KING", "KFC", "SUBWAY", "WENDY", "DOMINO", "PIZZA HUT",
            "CHAAYOS", "CHAI POINT", "FRESHMENU", "BOX8", "FAASOS",
            "REBEL FOODS", "OVEN STORY", "LUNCHBOX", "TACO BELL", "BASKIN",
            "NATURALS", "AMUL", "MILK BASKET", "COUNTRY DELIGHT",
            "EATSURE", "DINEOUT", "MAGICPIN", "DINING",
        ],
    ),
    (
        "Travel",
        [
            "IRCTC", "UBER", "OLA", "RAPIDO", "IXIGO", "MAKEMYTRIP", "REDBUS",
            "PETROL", "FUEL", "AIRPORT", "INDIGO", "SPICEJET", "AIR INDIA",
            "GOIBIBO", "YATRA", "HIGHWAY", "TOLL", "PARKING", "METRO",
            "RAILWAYS", "BUS", "CAB", "RIDE", "FLIGHT", "TRANSIT",
            "BPCL", "IOCL", "HPCL", "HP PETROL", "SHELL", "ESSAR OIL",
            "NAYARA", "RELIANCE PETRO", "PETRO", "DIESEL", "CNG",
            "OLA CABS", "RAPIDO BIKE", "INTERNATIO", "AIR TICKET",
            "AIRLINE", "BOARDING", "RAILWAY", "BUS TICKET", "TRAIN",
            "VISTARA", "AIRINDIA", "EMIRATES", "INDIGO AIR", "SPICE JET",
            "BLUE DART", "DTDC", "DELHIVERY", "EKART", "LOGISTIC",
            "TOLL PLAZA", "FASTAG", "NATIONAL HIGHWAY", "EXPRESSWAY",
        ],
    ),
    (
        "Shopping",
        [
            "AMAZON", "FLIPKART", "MYNTRA", "AJIO", "MEESHO", "NYKAA", "RETAIL",
            "SNAPDEAL", "SHOPSY", "TATACLIQ", "RELIANCE", "BIGBASKET",
            "DMART", "GROFERS", "JIOMART", "MARKET", "STORE", "MALL",
            "CROMA", "VIJAY SALES", "RELIANCE DIGITAL", "SAMSUNG STORE",
            "APPLE STORE", "ONEPLUS", "XIAOMI", "REALME", "OPPO",
            "LIFESTYLE", "WESTSIDE", "PANTALOONS", "SHOPPERS STOP",
            "CENTRAL MALL", "H&M", "ZARA", "FOREVER 21", "UNIQLO",
            "MAX FASHION", "V-MART", "EASYDAY", "SPAR", "HYPERCITY",
            "LENSKART", "PEPPERFRY", "URBAN LADDER", "IKEA", "GODREJ INTERIO",
            "PURPLLE", "MAMAEARTH", "PLUM", "SUGAR", "MCAFFEINE",
            "FIRSTCRY", "HOPSCOTCH", "BABYOYE", "MOTHERCARE",
        ],
    ),
    (
        "Utilities",
        [
            "ELECTRICITY", "BESCOM", "MSEB", "BSES", "TATA POWER", "GAS",
            "WATER BILL", "MAHADISCOM", "BIJLI", "TORRENT", "ADANI ELEC",
            "BILL PAYMENT", "UTILITY", "BBPS", "MUNICIPAL", "PROPERTY TAX",
            "TNEB", "WESCO", "CESU", "JVVNL", "UPPCL", "PSPCL",
            "DGVCL", "MGVCL", "UGVCL", "PGVCL", "HESCOM",
            "MGL", "IGL", "CGL", "MAHANAGAR GAS", "INDRAPRASTHA GAS",
            "SABARMATI GAS", "GUJARAT GAS", "ADANI GAS",
            "PIPED GAS", "LPG", "INDANE", "HP GAS", "BHARAT GAS",
            "WATER SUPPLY", "NMMC", "MCGM", "BBMP", "GHMC", "BMC",
            "SOLID WASTE", "SEWAGE", "DRAINAGE", "MAINTENANCE BILL",
        ],
    ),
    (
        "Telecom",
        [
            "AIRTEL", "JIO", "VODAFONE", "BSNL", "RECHARGE", "POSTPAID",
            "BROADBAND", "VI MOBILE", "IDEA", "TATA TELE", "MTNL",
            "INTERNET", "WIFI", "DTH", "TATASKY", "DISH TV", "SUN DIRECT",
            "PREPAID", "MOBILE RECHARGE", "AIRTEL PAYMENT", "JIO FIBER",
            "JIO RECHARGE", "VI RECHARGE", "AIRTEL RECHARGE",
            "TATA SKY", "D2H", "VIDEOCON D2H", "AIRTEL DTH",
            "HATHWAY", "ACT FIBERNET", "TIKONA", "SPECTRANET",
            "EXCITEL", "ASIANET", "NEXTRA", "I-ON", "TATAPLAY",
            "TELENOR", "RELIANCE JIO", "JIOCINEMA", "AIRTEL XSTREAM",
        ],
    ),
    (
        "Entertainment",
        [
            "NETFLIX", "HOTSTAR", "AMAZON PRIME", "SPOTIFY", "BOOKMYSHOW",
            "ZEE5", "YOUTUBE", "APPLE TV", "SONY LIV", "PRIME VIDEO",
            "VOOT", "MX PLAYER", "CINEPOLIS", "PVR", "INOX",
            "ENTERTAINMENT", "GAMING", "STEAM", "PLAYSTATION", "XBOX",
            "DISNEY", "DISNEY+", "HOTSTAR VIP", "ALT BALAJI", "ULLU",
            "LIONSGATE", "MUBI", "HUNGAMA", "GAANA", "WYNK", "JIOSAAVN",
            "APPLE MUSIC", "DEEZER", "TIDAL", "AUDIBLE",
            "PAYTM MOVIE", "CARNIVAL CINEMAS", "MIRAJ", "FUN CINEMAS",
            "GAME", "PUBG", "BATTLEGROUNDS", "DREAM11", "MPL", "FANTASY",
        ],
    ),
    (
        "Healthcare",
        [
            "PHARMACY", "APOLLO", "MEDPLUS", "HOSPITAL", "CLINIC", "DIAGNOSTIC",
            "NETMEDS", "PHARMEASY", "1MG", "TATA 1MG", "DOCTOR", "LAB TEST",
            "PATHOLOGY", "MEDICAL", "HEALTH", "WELLNESS", "NARAYANA",
            "FORTIS", "MAX HOSPITAL", "AIIMS", "MEDANTA", "MANIPAL",
            "RAINBOW", "CLOUDNINE", "MOTHERHOOD", "PRISTYN CARE",
            "LYBRATE", "PRACTO", "DOCPRIME", "MFINE", "PORTEA",
            "SRL DIAGNOSTICS", "METROPOLIS", "THYROCARE", "DR LAL",
            "MEDLIFE", "GENERICS", "CHEMIST", "DRUG STORE", "DISPENSARY",
            "NURSING HOME", "MATERNITY", "DENTAL", "EYE CARE", "OPTICIAN",
            "PHYSIOTHERAPY", "AYURVEDIC", "HOMEOPATHY", "OPD",
        ],
    ),
    (
        "Education",
        [
            "SCHOOL FEE", "COLLEGE", "UDEMY", "COURSERA", "BYJU", "UNACADEMY",
            "TUITION", "FEES", "ADMISSION", "EXAM", "CBSE", "BOARD FEE",
            "UNIVERSITY", "INSTITUTION", "COACHING", "VEDANTU", "TOPPR",
            "WHITEHAT", "EDTECH", "SCHOOL FEES", "ACADEMIC", "SEMESTER",
            "TUITION FEE", "LIBRARY FEE", "HOSTEL FEE", "MESS FEE",
            "UPGRAD", "SIMPLILEARN", "GREAT LEARNING", "SKILLSOFT",
            "PLURALSIGHT", "LINKEDIN LEARN", "KHAN ACADEMY",
            "TESTBOOK", "GRADEUP", "ADDA247", "MAHENDRA", "CAREER LAUNCHER",
            "IIT JEE", "NEET", "CLAT", "GMAT", "GRE", "IELTS", "TOEFL",
            "INTERNSHIP FEE", "CERTIFICATION", "TRAINING FEE",
        ],
    ),
    (
        "Investments",
        [
            "MUTUAL FUND", "SIP", "ZERODHA", "GROWW", "UPSTOX", "NSDL", "CDSL",
            "DEMAT", "NSE", "BSE", "KUVERA", "COIN", "PAYTM MONEY",
            "ANGEL", "IIFL", "HDFC SEC", "KOTAK SEC", "STOCK", "TRADING",
            "INVEST", "ETF", "PORTFOLIO", "MOTILAL OSWAL", "SHAREKHAN",
            "ICICI DIRECT", "KOTAK SECURITIES", "AXIS DIRECT",
            "NIPPON INDIA MF", "SBI MF", "HDFC MF", "ICICI PRUDENTIAL MF",
            "MIRAE ASSET", "AXIS MF", "FRANKLIN", "DSP", "INVESCO",
            "PPF", "ELSS", "FD", "FIXED DEPOSIT", "RD", "RECURRING DEP",
            "NPS", "NATIONAL PENSION", "SOVEREIGN GOLD", "GOLD ETF",
            "SMALLCASE", "WINDMILL", "PIGGY", "FISDOM", "SCRIPBOX",
        ],
    ),
    (
        "Insurance",
        [
            "LIC", "ICICI PRU", "HDFC LIFE", "SBI LIFE", "MAX LIFE", "PREMIUM",
            "POLICY", "BAJAJ ALLIANZ", "TATA AIG", "ORIENTAL INS",
            "RELIANCE GEN", "NEW INDIA", "TERM PLAN", "HEALTH INS",
            "MOTOR INS", "VEHICLE INS", "INSURANCE PREMIUM", "LIFE INS",
            "STAR HEALTH", "NIVA BUPA", "CARE HEALTH", "MANIPAL CIGNA",
            "BHARTI AXA", "KOTAK LIFE", "CANARA HSBC", "PNB METLIFE",
            "AEGON", "EDELWEISS", "FUTURE GENERALI", "SBI GENERAL",
            "CHOLAMANDALAM", "HDFC ERGO", "NATIONAL INS", "UNITED INDIA",
            "GIC", "ENDOWMENT", "MONEY BACK", "ULIP", "ANNUITY",
            "ACCIDENT INS", "TRAVEL INS", "MARINE INS", "CROP INS",
        ],
    ),
    (
        "Cash Withdrawal",
        [
            "ATM", "CASH WDL", "ATM WDL", "WITHDRAWAL", "CASH DEPOSIT",
            "CDM", "CASH ADVANCE", "ATM WITHDRAWAL", "CASH AT ATM",
            "ATM CASH", "CARDLESS CASH", "MICRO ATM",
        ],
    ),
    (
        "UPI / Transfer",
        [
            "UPI", "BHIM", "PHONEPE", "GPAY", "PAYTM", "NEFT", "IMPS", "RTGS",
            "TRANSFER", "SENT TO", "RECEIVED FROM", "P2P", "PAYMENT TO",
            "MONEY TRANSFER", "FUND TRANSFER", "BANK TRANSFER",
            "MOBILE BANKING", "NET BANKING", "INTERNET BANKING",
            "GOOGLE PAY", "PHONE PE", "AMAZON PAY", "WHATSAPP PAY",
            "TRUPAY", "MOBIKWIK", "FREECHARGE", "OXIGEN",
            "NEFT CR", "NEFT DR", "IMPS CR", "IMPS DR", "RTGS CR", "RTGS DR",
            "INWARD NEFT", "OUTWARD NEFT", "ACH CR", "ACH DR",
        ],
    ),
    (
        "Rent",
        [
            "RENT", "HOUSE RENT", "RENTAL", "TENANT", "LEASE", "LANDLORD",
            "PG", "ACCOMMODATION", "FLAT RENT", "SOCIETY", "MAINTENANCE",
            "HOUSING", "HOSTEL RENT", "ROOM RENT", "PAYING GUEST",
            "APARTMENT RENT", "VILLA RENT", "PROPERTY RENT",
            "MONTHLY RENT", "ADVANCE RENT", "SECURITY DEPOSIT",
            "BROKER FEE", "BROKERAGE", "SOCIETY CHARGES",
            "MAINTENANCE CHARGES", "COMMON AREA", "PARKING CHARGES",
            "BUILDING MAINT", "APARTMENT MAINT",
        ],
    ),
]

# Pre-compile all patterns for performance
_COMPILED_RULES: list[tuple[str, list[re.Pattern]]] = [
    (cat, [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords])
    for cat, keywords in CATEGORY_RULES
]


def categorize(description: str) -> str:
    """Return the best-matching category for a transaction description."""
    if not description:
        return "Other"

    desc_upper = description.upper()

    for category, patterns in _COMPILED_RULES:
        for pat in patterns:
            if pat.search(desc_upper):
                return category

    return "Other"


def categorize_all(transactions: list) -> None:
    """In-place categorization of a list of Transaction objects."""
    for txn in transactions:
        txn.category = categorize(txn.description)


def get_categorization_stats(transactions: list) -> dict:
    total = len(transactions)
    if total == 0:
        return {"total": 0, "categorized": 0, "uncategorized": 0, "pct_categorized": 0.0}
    uncategorized = sum(1 for t in transactions if t.category == "Other")
    categorized = total - uncategorized
    return {
        "total": total,
        "categorized": categorized,
        "uncategorized": uncategorized,
        "pct_categorized": round(categorized / total * 100, 1),
    }
