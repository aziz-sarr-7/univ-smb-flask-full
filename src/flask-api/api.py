from flask import Flask, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "data" / "webservers.json"


def load_webservers():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_webservers(webservers):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(webservers, f, indent=2, ensure_ascii=False)


@app.route("/")
def home():
    return jsonify({"message": "API Web Configurator"})


@app.route("/webservers", methods=["GET"])
def get_webservers():
    return jsonify(load_webservers())


@app.route("/webservers/<int:webserver_id>", methods=["GET"])
def get_webserver(webserver_id):
    webservers = load_webservers()

    for webserver in webservers:
        if webserver["id"] == webserver_id:
            return jsonify(webserver)

    return jsonify({"error": "Serveur web introuvable"}), 404


@app.route("/webservers", methods=["POST"])
def create_webserver():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON manquant"}), 400

    required_fields = ["server_name", "listen", "root"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Champ manquant : {field}"}), 400

    webservers = load_webservers()

    new_id = 1
    if webservers:
        new_id = max(webserver["id"] for webserver in webservers) + 1

    new_webserver = {
        "id": new_id,
        "server_name": data["server_name"],
        "listen": int(data["listen"]),
        "root": data["root"]
    }

    webservers.append(new_webserver)
    save_webservers(webservers)

    return jsonify(new_webserver), 201


@app.route("/webservers/<int:webserver_id>", methods=["DELETE"])
def delete_webserver(webserver_id):
    webservers = load_webservers()

    for webserver in webservers:
        if webserver["id"] == webserver_id:
            webservers.remove(webserver)
            save_webservers(webservers)
            return jsonify({"message": "Serveur web supprimé avec succès"})

    return jsonify({"error": "Serveur web introuvable"}), 404