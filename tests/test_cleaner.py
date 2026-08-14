# tests/test_cleaner.py
from datetime import date
from app.services.cleaner_service import cleaner_service
from app.core.security import sanitize_csv_cell

def test_csv_injection_mitigation():
    # Detect formula triggers and prepend single quote
    assert sanitize_csv_cell("=CMD|'calc'!A0") == "'=CMD|'calc'!A0"
    assert sanitize_csv_cell("@SUM(1+1)") == "'@SUM(1+1)"
    assert sanitize_csv_cell("+4412345") == "'+4412345"
    assert sanitize_csv_cell("Normal Text") == "Normal Text"

def test_date_cleaning_variations():
    expected = date(2022, 10, 15)
    assert cleaner_service.clean_date("2022-10-15") == expected
    assert cleaner_service.clean_date("10/15/2022") == expected
    assert cleaner_service.clean_date("October 15, 2022") == expected
    assert cleaner_service.clean_date("InvalidDateString") is None

def test_phone_and_email_cleaning():
    assert cleaner_service.clean_email("  TEST.USER@Domain.COM  ") == "test.user@domain.com"
    assert cleaner_service.clean_email("bad-email-address") is None
    # Assuming default US region
    assert cleaner_service.clean_phone("415-555-2671") == "+14155552671"
