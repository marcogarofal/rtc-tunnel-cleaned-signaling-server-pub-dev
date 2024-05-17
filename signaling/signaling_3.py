from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from urllib.parse import urlparse, unquote

app = Flask(__name__)
socketio = SocketIO(app)

# Utenti hard-coded per l'esempio
valid_users = {'user': 'password'}

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

def extract_credentials_from_url(url):
    parsed_url = urlparse(url)
    username = unquote(parsed_url.username) if parsed_url.username else None
    password = unquote(parsed_url.password) if parsed_url.password else None
    return username, password

def authenticate_user(username, password):
    return valid_users.get(username) == password

@socketio.on('connect')
def handle_connect():
    username, password = extract_credentials_from_url(request.url)
    if username and password and authenticate_user(username, password):
        print(f'Authenticated user: {username}')
    else:
        print('Authentication failed')

@app.route('/topic/message/server', methods=['GET'])
def handle_server_message():
    # Implementa qui la logica per gestire la richiesta del client
    return jsonify({"message": "Hello from the server"})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
