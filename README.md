# rtc-tunnel-cleaned-signaling-server (signaling_12.py ultima versione, con la gestione del topic e stun server)

problema se ci sono 2 topic tra 2 gruppi uguali, in quel caso tendono a sovrapporsi, i topic devono essere univoci
### idea per risolvere: creare coppie di topic tuples e inoltrare i messaggi solo tra le coppie (per esempio: topic1-topic2, quando ricevo messaggio topic1 inoltro a topic2 e basta, e viceversa)

## signaling + stun server
python3 signaling_12.py
python3 server.py 

### tunnel
python3 server.py -w -u http://127.0.0.1:8080 -r ws://127.0.0.1:8080 --topic topic1 -n 127.0.0.1:3478

python3 client.py -s 5000 -d 5001 -w -u http://127.0.0.1:8080 -r ws://127.0.0.1:8080 --topic topic1 -n 127.0.0.1:3478



python3 server.py -w -u http://127.0.0.1:8080 -r ws://127.0.0.1:8080 --topic topic1

python3 client.py -s 5000 -d 5000 -w -u http://127.0.0.1:8080 -r ws://127.0.0.1:8080 --topic topic1


