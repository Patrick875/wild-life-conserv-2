from extensions import db
import time

class BaseModel(db.Model):
    __abstract__=True

    id=db.Column(db.Integer,primary_key=True)

    created_at=db.Column(
        db.BigInteger,
        default=lambda: int(time.time()),
        nullable=False)
    
    updated_at=db.Column(
         db.BigInteger,
        default=lambda: int(time.time()),
        onupdate=lambda: int(time.time()),
        nullable=False)
   
    

