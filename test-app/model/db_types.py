"""
Custom SQLAlchemy types
"""
from typing import Optional
from datetime import datetime, timezone

from model.sqlalchemy import db


class IntEnum(db.TypeDecorator):
    """
    Useful for existing tables where an integer
    column represents an enum
    """

    impl = db.Integer

    def __init__(self, enumtype, *args, **kwargs) -> None:
        """
        Initialization
        """
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        """
        Value stored in db.
        """
        if value is not None:
            value = value.value
        return value

    def process_result_value(self, value, dialect):
        """
        Value returned on attribute access.
        """
        if value is not None:
            value = self._enumtype(value)
        return value


class UTCDateTime(db.TypeDecorator):
    """
    We store timestamps as naive utc datetimes.
    """

    impl = db.DateTime

    def process_bind_param(self, value, dialect) -> Optional[datetime]:
        """
        If no tzinfo is specified utc is assumed and datetime
        is saved to db with no changes.
        If tzinfo is not utc convert it to utc
        before saving in db.
        """
        if value is not None:
            if value.tzinfo:
                value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect) -> Optional[datetime]:
        """
        Return value as utc datetime.
        """
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value
