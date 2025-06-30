from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/payments/pix', methods=['POST'])
def create_pix_payment():
    return jsonify({ "message": 'The payment has been created'})

@app.route('/payments/pix/confimation', methods=['POST'])
def pix_confirmation():
    return jsonify({ "message": 'The payment has been confirmed'})

@app.route('/payments/pix/<string:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    return jsonify({ "message": 'Payment pix'})

if __name__ == '__main__':
    app.run(debug=True, port=3333)