from django.db.backends.mysql.operations import DatabaseOperations as MySQLOps
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings


class DatabaseOperations(MySQLOps):
    def convert_datetimefield_value(self, value, expression, connection):
        if isinstance(value, str):
            dt = parse_datetime(value)
            if dt is None:
                return None
            if settings.USE_TZ:
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
                return dt
        return super().convert_datetimefield_value(value, expression, connection)
