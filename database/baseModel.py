from datetime import datetime,UTC

from extensions import db


def utc_timestamp_ms():
    return int(datetime.now(UTC).timestamp() * 1000)

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.BigInteger,
        default=utc_timestamp_ms,
        nullable=False,
    )

    updated_at = db.Column(
        db.BigInteger,
        default=utc_timestamp_ms,
        onupdate=utc_timestamp_ms,
        nullable=False,
    )

