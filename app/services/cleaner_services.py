# app/services/cleaner_service.py
import re
from datetime import datetime
from dateutil import parser as date_parser
import phonenumbers
from typing import Optional, Tuple
from app.core.security import sanitize_csv_cell
from app.config import settings

class CleanerService:
    @staticmethod
    def clean_name(raw_name: str) -> str:
        """Strips whitespace, sanitizes formula triggers, and title cases."""
        if not raw_name or not isinstance(raw_name, str):
            return ""
        sanitized = sanitize_csv_cell(raw_name)
        return sanitized.strip().title()

    @staticmethod
    def clean_email(raw_email: str) -> Optional[str]:
        """Validates and lowercases email addresses."""
        if not raw_email or not isinstance(raw_email, str):
            return None
        email = raw_email.strip().lower()
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return email if re.match(pattern, email) else None

    @staticmethod
    def clean_phone(raw_phone: str) -> Optional[str]:
        """Parses mixed international/national formats into standardized E.164 string."""
        if not raw_phone or not isinstance(raw_phone, str):
            return None
        try:
            parsed = phonenumbers.parse(raw_phone.strip(), settings.DEFAULT_PHONE_REGION)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            return None
        except Exception:
            return None

    @staticmethod
    def clean_date(raw_date: str) -> Optional[datetime.date]:
        """Robust multi-format date parser returning uniform YYYY-MM-DD date objects."""
        if not raw_date or not isinstance(raw_date, str):
            return None
        try:
            # Handles '12/05/2021', '2021-05-12', 'May 12, 2021', etc.
            dt = date_parser.parse(raw_date.strip())
            return dt.date()
        except Exception:
            return None

cleaner_service = CleanerService()
