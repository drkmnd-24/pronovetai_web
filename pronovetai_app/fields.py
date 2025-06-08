# pronovetai_app/fields.py   (or anywhere import-able)
from decimal import Decimal, InvalidOperation
from django.db import models


class BlankZeroIntegerField(models.IntegerField):
    """
    Same as IntegerField but treats '' (empty string) and '0' coming from a
    legacy MySQL table as NULL/None.
    """
    description = "IntegerField that tolerates '' coming from MySQL"

    def from_db_value(self, value, expression, connection):
        # DB → Python (SELECT)
        if value in ("", None):
            return None
        return int(value)

    def to_python(self, value):
        # Admin / forms → Python
        if value in ("", None):
            return None
        return super().to_python(value)


class BlankZeroDecimalField(models.DecimalField):
    """
    DecimalField version: turns '' into None and safely converts strings that
    only contain whitespace.
    """
    description = "DecimalField that tolerates '' coming from MySQL"

    def from_db_value(self, value, expression, connection):
        if value in ("", None):
            return None
        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, TypeError):
            return None           # fall back to NULL

    def to_python(self, value):
        if value in ("", None):
            return None
        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, TypeError):
            return None
