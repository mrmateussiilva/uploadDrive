from flask import Flask, send_file
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)

@app.get("/playlist.m3u")
def playlist():
    return send_file("playlist.m3u", mimetype="audio/x-mpegurl")

@app.get("/")
def home():
    return "Servidor de Playlist funcionando!"

# ADAPTAR FLASK → ASGI PARA O UVICORN
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)

