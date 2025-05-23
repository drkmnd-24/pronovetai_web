from django.db.backends.mysql.operations import DatabaseOperations as MySQLOps
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings


class DatabaseOperations(MySQLOps):
    def convert_datetimefield_value(self, value, expression, connection):
        if isinstance(value, str):
            if value.startswith('0000-00-00'):
                return None

            dt = parse_datetime(value)
            if not dt:
                return None

            if settings.USE_TZ:
                tz = getattr(connection, 'timezone', timezone.get_current_timezone())
                dt = timezone.make_aware(dt, tz)
            return dt

        return super().convert_datetimefield_value(value, expression, connection)
