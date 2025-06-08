# pronovetai_app/fields.py
from decimal import Decimal, InvalidOperation
from django.db import models


class BlankZeroIntegerField(models.IntegerField):
    """
    IntegerField tolerant of legacy data:
      • ''  → None
      • '0' → None   (if you keep that rule)
      • any non-numeric junk like '1 basement' → None
    """
    description = "IntegerField that tolerates messy MySQL strings"

    def _clean_int(self, value):
        # keep only leading digits, drop the rest
        digits = "".join(ch for ch in str(value).lstrip() if ch.isdigit() or ch in "+-")
        return int(digits) if digits else None

    def from_db_value(self, value, expression, connection):
        if value in ("", None, "0"):
            return None
        try:
            return self._clean_int(value)
        except (ValueError, TypeError):
            return None

    def to_python(self, value):
        if value in ("", None, "0"):
            return None
        try:
            return self._clean_int(value)
        except (ValueError, TypeError):
            return None


class BlankZeroDecimalField(models.DecimalField):
    """
    DecimalField tolerant of legacy '' / weird text.
    """
    description = "DecimalField that tolerates messy MySQL strings"

    def _clean_dec(self, value):
        # strip spaces; keep only first numeric part
        txt = str(value).strip()
        # allow leading sign and dot
        allowed = set("0123456789+-eE.")
        cleaned = "".join(ch for ch in txt if ch in allowed)
        return Decimal(cleaned) if cleaned else None

    def from_db_value(self, value, expression, connection):
        if value in ("", None):
            return None
        try:
            return self._clean_dec(value)
        except (InvalidOperation, ValueError, TypeError):
            return None

    def to_python(self, value):
        if value in ("", None):
            return None
        try:
            return self._clean_dec(value)
        except (InvalidOperation, ValueError, TypeError):
            return None
