from flask import Flask, jsonify, request, send_file, render_template
from repository.database import db
from models.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix
from uuid import UUID
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)
socketio = SocketIO(app)

@app.route('/payments/pix', methods=['POST'])
def create_pix_payment():
    data = request.get_json()

    if 'value' not in data:
        return jsonify({ 'error': 'Value is required' }), 400

    expiration_date = datetime.now() + timedelta(minutes=30)

    new_payment = Payment(
        value=data['value'],
        expiration_date=expiration_date,
    )

    pix_obj = Pix()
    data_payment_pix = pix_obj.create_payment()
    new_payment.bank_payment_id = data_payment_pix['bank_payment_id']
    new_payment.qr_code = data_payment_pix['qr_code_path']

    db.session.add(new_payment)
    db.session.commit()

    return jsonify({
        "message": 'The payment has been created',
        "payment": new_payment.to_dict(),
    })

@app.route('/payments/pix/confimation', methods=['POST'])
def pix_confirmation():
    data = request.get_json()

    if 'bank_payment_id' not in data and "value" not in data:
        return jsonify({ 'error': 'Invalid payment data' }), 400

    payment = Payment.query.filter_by(
        bank_payment_id=data.get('bank_payment_id')
    ).first()

    if not payment:
        return jsonify({ 'error': 'Payment not found' }), 404
    
    if payment.paid:
        return jsonify({ 'error': 'The payment has already been confirmed' }), 400
    
    if data.get('value') != payment.value:
        return jsonify({ 'error': 'Invalid payment data' }), 400

    if payment.expiration_date < datetime.now():
        return jsonify({ 'error': 'The payment has expired' }), 400
    
    payment.paid = True
    db.session.commit()
    socketio.emit(f'payment-confirmed-{payment.id}')

    return jsonify({ 'message': 'The payment has been confirmed' })

@app.route('/payments/pix/<string:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    try:
        uuid_payment_id = UUID(payment_id)
    except ValueError:
        return render_template('404.html'), 404

    payment = Payment.query.get(uuid_payment_id)

    if not payment:
        return render_template('404.html'), 404
    
    if payment.paid:
        return render_template(
            'confirmed_payment.html',
            value=payment.value,
            payment_number=payment.payment_number,
            payment=payment,
        )

    if not payment:
        return render_template('404.html'), 404

    return render_template(
        'payment.html',
        payment_id=payment.id,
        value=payment.value,
        payment_number=payment.payment_number,
        host="http://localhost:5000",
        qr_code=payment.qr_code
    )

# websockets
@socketio.on('connect')
def handle_connect():
    print('Client connected to the server')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from the server')

@app.route('/payments/pix/qr_code/<file_name>', methods=['GET'])
def get_qr_code(file_name):
    return send_file(f"static/img/{file_name}.png", mimetype="image/png")

if __name__ == '__main__':
    socketio.run(app, debug=True)