from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, send, emit
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import logging

app = Flask(__name__)

# Configura il logger per registrare i dettagli delle richieste HTTP
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

app.secret_key = 'your_secret_key'
socketio = SocketIO(app)
login_manager = LoginManager(app)

# Simuliamo MessageService come un'archiviazione in memoria
sessions = {}

# Utenti hard-coded per esempio
users = {'user': {'password': 'password'}}

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(username):
    if username in users:
        user = User()
        user.id = username
        return user

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and password == users[username]['password']:
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('dashboard'))
    return 'Login failed'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/message/<destination>', methods=['POST'])
@login_required
def send_message(destination):
    message = request.data.decode('utf-8')
    if destination in sessions:
        socketio.emit('message', message, room=destination)
        return '', 200
    else:
        return '', 404

@socketio.on('connect')
def handle_connect():
    session_id = request.sid
    destination = session_id.split('/')[-1]  # Estrazione della destinazione dall'id sessione
    sessions[destination] = session_id
    print(f'Client {destination} connesso')

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    destination = session_id.split('/')[-1]  # Estrazione della destinazione dall'id sessione
    sessions.pop(destination, None)
    print(f'Client {destination} disconnesso')

@app.route('/state')
@login_required
def get_state():
    return jsonify(list(sessions.keys()))


#@app.route('/topic/message/<destination>', methods=['GET'])
#def topic_message(destination):
    #Qui puoi inserire la logica per gestire la richiesta
    #return 'Topic message for ' + destination

# Funzione per gestire la richiesta GET a "/topic/message/server"
@app.route('/topic/message/<destination>', methods=['GET'])
def get_message(destination):
    print("qui")
    # Esempio di logica per gestire la richiesta GET
    if destination in sessions:
        return jsonify({"destination": destination, "message": "Example message"})
    else:
        return jsonify({"error": "Destination not found"}), 404



@app.route('/topic/message/server', methods=['GET'])
def handle_server_message():
    print("qui2")
    # Implementa qui la logica per gestire la richiesta del client
    return jsonify({"message": "Hello from the server"})


@app.route('/message/topic', methods=['POST'])
@login_required
def send_message_to_topic():
    message = request.data.decode('utf-8')
    # Implementa qui la logica per gestire il messaggio inviato a /message/topic
    print(f"Received message for topic: {message}")
    # Qui potresti inviare il messaggio tramite SocketIO o eseguire altre operazioni necessarie
    return '', 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
