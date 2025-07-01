from repository.database import db
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID, NUMERIC
from datetime import datetime
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = db.Column(db.Integer, nullable=False, unique=True)
    value = db.Column(NUMERIC(10, 2), nullable=False)
    paid = db.Column(db.Boolean, default=False)
    bank_payment_id = db.Column(db.Integer, nullable=True)
    qr_code = db.Column(db.String(255), nullable=True)
    expiration_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "payment_number": self.payment_number,
            "value": float(self.value),
            "paid": self.paid,
            "bank_payment_id": self.bank_payment_id,
            "qr_code": self.qr_code,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

@event.listens_for(Payment, 'before_insert')
def generate_payment_number(mapper, connect, target):
    result = db.session.query(db.func.max(Payment.payment_number)).scalar()
    target.payment_number = (result or 0) + 1
