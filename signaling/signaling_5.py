from flask import Flask, render_template
from flask_socketio import SocketIO, Namespace

app = Flask(__name__)
socketio = SocketIO(app)

# Definisci un namespace personalizzato per il percorso WebSocket
class MyNamespace(Namespace):
    def on_connect(self):
        print('WebSocket client connected')

    def on_disconnect(self):
        print('WebSocket client disconnected')

    def on_message(self, message):
        print('Messaggio ricevuto:', message)
        # Inserisci qui la logica per gestire il messaggio ricevuto

# Associa il namespace al percorso WebSocket desiderato
socketio.on_namespace(MyNamespace('/topic/message/server'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8080)
