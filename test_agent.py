from pathlib import Path

from tools import (
    find_latest_invoice,
    read_invoice,
    extract_invoice_data,
    verify_invoice,
    validate_invoice_totals
)


passed = 0
failed = 0


def check(test_name, condition):
    global passed, failed

    if condition:
        print(f"[PASS] {test_name}")
        passed += 1
    else:
        print(f"[FAIL] {test_name}")
        failed += 1


print()
print("======================================")
print(" AUTONOMOUS INVOICE AGENT EVALUATION")
print("======================================")
print()


# ------------------------------------------------
# TEST 1: FIND VALID INVOICE
# ------------------------------------------------

invoice_path = find_latest_invoice(
    "ABC Technologies"
)

check(
    "Find valid ABC invoice",
    invoice_path is not None
)


# ------------------------------------------------
# TEST 2: READ INVOICE
# ------------------------------------------------

if invoice_path:

    invoice_text = read_invoice(
        invoice_path
    )

    check(
        "Read invoice successfully",
        len(invoice_text) > 0
    )

else:

    invoice_text = ""


# ------------------------------------------------
# TEST 3: EXTRACT DATA
# ------------------------------------------------

invoice_data = extract_invoice_data(
    invoice_text
)

check(
    "Extract invoice number",
    invoice_data.get("Invoice Number")
    == "ABC-2026-001"
)

check(
    "Extract vendor",
    "ABC Technologies"
    in invoice_data.get("Vendor", "")
)


# ------------------------------------------------
# TEST 4: VALIDATE INVOICE
# ------------------------------------------------

validation_result = validate_invoice_totals(
    invoice_data
)

check(
    "Validate invoice financial information",
    validation_result is True
)


# ------------------------------------------------
# TEST 5: INVALID INVOICE
# ------------------------------------------------

bad_invoice = Path(
    "invoices/delta_bad_invoice.txt"
)

if bad_invoice.exists():

    bad_text = read_invoice(
        bad_invoice
    )

    bad_data = extract_invoice_data(
        bad_text
    )

    bad_validation = validate_invoice_totals(
        bad_data
    )

    check(
        "Reject invalid invoice totals",
        bad_validation is False
    )

else:

    print(
        "[SKIP] Invalid invoice test file not found"
    )


# ------------------------------------------------
# TEST 6: DUPLICATE / VERIFICATION
# ------------------------------------------------

if invoice_data.get("Invoice Number"):

    verification = verify_invoice(
        invoice_data
    )

    check(
        "Verify invoice against company system",
        verification is True
    )


# ------------------------------------------------
# FINAL RESULT
# ------------------------------------------------

print()
print("======================================")
print(" EVALUATION RESULT")
print("======================================")

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
)

print()

if failed == 0:

    print(
        "ALL TESTS PASSED"
    )

else:

    print(
        "SOME TESTS FAILED"
    )