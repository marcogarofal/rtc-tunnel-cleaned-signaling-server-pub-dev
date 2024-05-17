from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import Flask, request, jsonify

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    emit('response', 'Message received: ' + message)

@app.route('/server', methods=['GET'])
def handle_server_request():
    print("qui")
    auth = request.args.get('auth')
    # Verifica l'autenticazione qui
    if auth == 'dXNlcm5hbWU6cGFzc3dvcmQ=':  # Esempio di autenticazione base64
        return jsonify({'message': 'Authenticated successfully'}), 200
    else:
        return jsonify({'error': 'Authentication failed'}), 401


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
