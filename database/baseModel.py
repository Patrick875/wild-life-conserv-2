from datetime import datetime, timezone

from extensions import db

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.BigInteger,
        default=lambda: datetime.now().timestamp(),
        server_default=db.func.now().timestamp(),
        nullable=False,
    )

    updated_at = db.Column(
        db.BigInteger,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now().timestamp(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

