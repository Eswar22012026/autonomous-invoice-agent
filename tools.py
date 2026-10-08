from pathlib import Path
from datetime import datetime
import json
import re

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


INVOICE_FOLDER = Path("invoices")
COMPANY_SYSTEM_FILE = Path("company_system.json")


def parse_invoice_date(text):
    """Convert common invoice date formats into a comparable date."""

    if not text:
        return datetime.min

    text = str(text).strip()

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    return datetime.min


def find_latest_invoice(vendor_name):
    """
    Find the latest invoice for a vendor.

    If two files have the same invoice date,
    PDF is preferred over TXT.
    """

    if not INVOICE_FOLDER.exists():
        return None

    vendor_words = [
        word.lower()
        for word in vendor_name.split()
        if len(word) > 2
    ]

    candidates = []

    for path in INVOICE_FOLDER.iterdir():

        if path.suffix.lower() not in [".txt", ".pdf"]:
            continue

        filename_lower = path.name.lower()

        if not any(
            word in filename_lower
            for word in vendor_words
        ):
            continue

        try:
            text = read_invoice(path)
        except Exception:
            continue

        vendor_match = re.search(
            r"Vendor:\s*(.+)",
            text,
            re.IGNORECASE
        )

        if vendor_match:
            invoice_vendor = vendor_match.group(1).strip().lower()

            if not any(
                word in invoice_vendor
                for word in vendor_words
            ):
                continue

        date_match = re.search(
            r"Invoice Date:\s*(.+)",
            text,
            re.IGNORECASE
        )

        invoice_date = datetime.min

        if date_match:
            invoice_date = parse_invoice_date(
                date_match.group(1)
            )

        pdf_priority = 1 if path.suffix.lower() == ".pdf" else 0

        candidates.append(
            (
                invoice_date,
                pdf_priority,
                path
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    return candidates[0][2]


def read_invoice(invoice_path):
    """Read invoice text from TXT or PDF."""

    invoice_path = Path(invoice_path)

    if invoice_path.suffix.lower() == ".txt":

        return invoice_path.read_text(
            encoding="utf-8"
        )

    if invoice_path.suffix.lower() == ".pdf":

        if PdfReader is None:
            raise RuntimeError(
                "pypdf is required to read PDF files."
            )

        reader = PdfReader(
            str(invoice_path)
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    raise ValueError(
        "Unsupported invoice file type."
    )


def get_value_after_label(text, label):
    """Extract a value appearing after a label."""

    pattern = re.compile(
        rf"{re.escape(label)}\s*:\s*(.+)",
        re.IGNORECASE
    )

    match = pattern.search(text)

    if match:
        return match.group(1).strip()

    return None


def extract_invoice_data(invoice_text):
    """
    Extract structured information from an invoice.

    Supports both simple TXT invoices and
    realistic PDF invoices.
    """

    data = {}

    # ------------------------------------------------
    # BASIC INFORMATION
    # ------------------------------------------------

    labels = [
        "Vendor",
        "Invoice Number",
        "Invoice Date",
        "Due Date",
        "PO Number",
        "Payment Terms",
        "Place of Supply",
        "Vendor GSTIN",
        "Vendor PAN",
        "Bill To",
        "Ship To",
        "Customer GSTIN",
        "Subtotal",
        "Discount",
        "Taxable Value",
        "CGST @ 9%",
        "SGST @ 9%",
        "Grand Total",
        "Amount in Words",
        "Bank Details",
        "Payment Status",
    ]

    for label in labels:

        value = get_value_after_label(
            invoice_text,
            label
        )

        if value:
            data[label] = value

    # ------------------------------------------------
    # PDF / REALISTIC INVOICE GSTIN VARIATIONS
    # ------------------------------------------------

    if "Vendor GSTIN" not in data:

        match = re.search(
            r"Vendor GSTIN\s*[:\-]?\s*([A-Z0-9]+)",
            invoice_text,
            re.IGNORECASE
        )

        if match:
            data["Vendor GSTIN"] = match.group(1)

    if "Customer GSTIN" not in data:

        match = re.search(
            r"(?:Customer|Bill To|Ship To).*?GSTIN\s*[:\-]?\s*([A-Z0-9]+)",
            invoice_text,
            re.IGNORECASE
        )

        if match:
            data["Customer GSTIN"] = match.group(1)

    # ------------------------------------------------
    # COMMON SIMPLE-INVOICE AMOUNT FORMAT
    # ------------------------------------------------

    if "Amount" in invoice_text:

        amount = get_value_after_label(
            invoice_text,
            "Amount"
        )

        if amount:
            data["Amount"] = amount

    # ------------------------------------------------
    # LINE ITEMS
    # ------------------------------------------------

    line_items = []

    item_pattern = re.compile(
        r"Item\s*:\s*(.+?)\s*\|\s*"
        r"Qty\s*:\s*(.+?)\s*\|\s*"
        r"Unit Price\s*:\s*(.+?)\s*\|\s*"
        r"Taxable\s*:\s*(.+)",
        re.IGNORECASE
    )

    for match in item_pattern.finditer(
        invoice_text
    ):

        line_items.append(
            {
                "Item": match.group(1).strip(),
                "Qty": match.group(2).strip(),
                "Unit Price": match.group(3).strip(),
                "Taxable": match.group(4).strip(),
            }
        )

    if line_items:
        data["Line Items"] = line_items

    # ------------------------------------------------
    # REALISTIC PDF TABLE EXTRACTION
    # ------------------------------------------------

    if not line_items:

        table_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"([\d,]+(?:\.\d+)?)\s*$",
            re.MULTILINE
        )

        for match in table_pattern.finditer(
            invoice_text
        ):

            line_items.append(
                {
                    "S.No": match.group(1),
                    "Item": match.group(2).strip(),
                    "Qty": match.group(3),
                    "Unit Price": match.group(4),
                    "Taxable": match.group(5),
                }
            )

        if line_items:
            data["Line Items"] = line_items

    return data


def save_invoice(invoice_data):
    """
    Save invoice information into the simulated
    company system.

    Prevent duplicate invoice numbers.
    """

    if not COMPANY_SYSTEM_FILE.exists():

        system = {
            "invoices": []
        }

    else:

        with open(
            COMPANY_SYSTEM_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            system = json.load(file)

    if "invoices" not in system:
        system["invoices"] = []

    invoice_number = invoice_data.get(
        "Invoice Number"
    )

    for existing_invoice in system["invoices"]:

        if existing_invoice.get(
            "Invoice Number"
        ) == invoice_number:

            return False

    system["invoices"].append(
        invoice_data
    )

    with open(
        COMPANY_SYSTEM_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            system,
            file,
            indent=4,
            ensure_ascii=False
        )

    return True


def verify_invoice(invoice_data):
    """
    Verify that every extracted field matches
    the saved company-system record.
    """

    if not COMPANY_SYSTEM_FILE.exists():
        return False

    with open(
        COMPANY_SYSTEM_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        system = json.load(file)

    invoice_number = invoice_data.get(
        "Invoice Number"
    )

    for saved_invoice in system.get(
        "invoices",
        []
    ):

        if saved_invoice.get(
            "Invoice Number"
        ) == invoice_number:

            for key, value in invoice_data.items():

                if saved_invoice.get(key) != value:
                    return False

            return True

    return False


def validate_invoice_totals(invoice_data):
    """
    Check whether the invoice financial totals
    are mathematically correct.

    Taxable Value + CGST + SGST = Grand Total

    For simple invoices that only contain
    an 'Amount' field, the function accepts
    the invoice because there are no tax
    components available to calculate.
    """

    # ------------------------------------------------
    # FULL FINANCIAL VALIDATION
    # ------------------------------------------------

    required_fields = [
        "Taxable Value",
        "CGST @ 9%",
        "SGST @ 9%",
        "Grand Total"
    ]

    if all(
        field in invoice_data
        for field in required_fields
    ):

        try:

            taxable_value = float(
                invoice_data["Taxable Value"]
                .replace("INR", "")
                .replace(",", "")
                .strip()
            )

            cgst = float(
                invoice_data["CGST @ 9%"]
                .replace("INR", "")
                .replace(",", "")
                .strip()
            )

            sgst = float(
                invoice_data["SGST @ 9%"]
                .replace("INR", "")
                .replace(",", "")
                .strip()
            )

            grand_total = float(
                invoice_data["Grand Total"]
                .replace("INR", "")
                .replace(",", "")
                .strip()
            )

            calculated_total = (
                taxable_value
                + cgst
                + sgst
            )

            return round(
                calculated_total,
                2
            ) == round(
                grand_total,
                2
            )

        except (
            KeyError,
            ValueError,
            AttributeError
        ):

            return False

    # ------------------------------------------------
    # SIMPLE INVOICE
    # ------------------------------------------------

    if "Amount" in invoice_data:

        return True

    return False