from repository.database import db
import uuid

class Payment(db.Model):
  __tablename__ = 'payments'
  id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
  value = db.Column(db.Float, nullable=False)
  paid = db.Column(db.Boolean, default=False)
  bank_payment_id = db.Column(db.Integer, nullable=True)
  qr_code = db.Column(db.String, nullable=True)
  expiration_date = db.Column(db.DateTime, nullable=False)
  created_at = db.Column(db.DateTime, server_default=db.func.now())