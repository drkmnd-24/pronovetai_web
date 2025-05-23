from django.db.backends.mysql import base as mysql_base
from .operations import DatabaseOperations


class DatabaseWrapper(mysql_base.DatabaseWrapper):
    ops_class = DatabaseOperations
