from flask import Flask, jsonify, request
import json
from pathlib import Path
LOADBALANCER_FILE = Path(__file__).parent / "data" / "loadbalancer.json"
app = Flask(__name__)

WEBSERVERS_FILE = Path(__file__).parent / "data" / "webservers.json"
REVERSEPROXIES_FILE = Path(__file__).parent / "data" / "reverseproxies.json"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route("/")
def home():
    return jsonify({"message": "API Web Configurator"})


# --------------------
# WEBSERVERS
# --------------------

@app.route("/webservers", methods=["GET"])
def get_webservers():
    return jsonify(load_json(WEBSERVERS_FILE))


@app.route("/webservers/<int:webserver_id>", methods=["GET"])
def get_webserver(webserver_id):
    webservers = load_json(WEBSERVERS_FILE)

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

    webservers = load_json(WEBSERVERS_FILE)

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
    save_json(WEBSERVERS_FILE, webservers)

    return jsonify(new_webserver), 201


@app.route("/webservers/<int:webserver_id>", methods=["DELETE"])
def delete_webserver(webserver_id):
    webservers = load_json(WEBSERVERS_FILE)

    for webserver in webservers:
        if webserver["id"] == webserver_id:
            webservers.remove(webserver)
            save_json(WEBSERVERS_FILE, webservers)
            return jsonify({"message": "Serveur web supprimé avec succès"})

    return jsonify({"error": "Serveur web introuvable"}), 404


# --------------------
# REVERSE PROXIES
# --------------------

@app.route("/reverseproxies", methods=["GET"])
def get_reverseproxies():
    return jsonify(load_json(REVERSEPROXIES_FILE))


@app.route("/reverseproxies/<int:reverseproxy_id>", methods=["GET"])
def get_reverseproxy(reverseproxy_id):
    reverseproxies = load_json(REVERSEPROXIES_FILE)

    for reverseproxy in reverseproxies:
        if reverseproxy["id"] == reverseproxy_id:
            return jsonify(reverseproxy)

    return jsonify({"error": "Reverse proxy introuvable"}), 404


@app.route("/reverseproxies", methods=["POST"])
def create_reverseproxy():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON manquant"}), 400

    required_fields = ["server_name", "listen", "proxy_pass"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Champ manquant : {field}"}), 400

    reverseproxies = load_json(REVERSEPROXIES_FILE)

    new_id = 1
    if reverseproxies:
        new_id = max(reverseproxy["id"] for reverseproxy in reverseproxies) + 1

    new_reverseproxy = {
        "id": new_id,
        "server_name": data["server_name"],
        "listen": int(data["listen"]),
        "proxy_pass": data["proxy_pass"]
    }

    reverseproxies.append(new_reverseproxy)
    save_json(REVERSEPROXIES_FILE, reverseproxies)

    return jsonify(new_reverseproxy), 201


@app.route("/reverseproxies/<int:reverseproxy_id>", methods=["DELETE"])
def delete_reverseproxy(reverseproxy_id):
    reverseproxies = load_json(REVERSEPROXIES_FILE)

    for reverseproxy in reverseproxies:
        if reverseproxy["id"] == reverseproxy_id:
            reverseproxies.remove(reverseproxy)
            save_json(REVERSEPROXIES_FILE, reverseproxies)
            return jsonify({"message": "Reverse proxy supprimé avec succès"})

    return jsonify({"error": "Reverse proxy introuvable"}), 404

@app.route("/loadbalancers", methods=["GET"])
def get_loadbalancers():
    return jsonify(load_json(LOADBALANCER_FILE))


@app.route("/loadbalancers/<int:loadbalancer_id>", methods=["GET"])
def get_loadbalancer(loadbalancer_id):
    loadbalancers = load_json(LOADBALANCER_FILE)

    for loadbalancer in loadbalancers:
        if loadbalancer["id"] == loadbalancer_id:
            return jsonify(loadbalancer)

    return jsonify({"error": "Load balancer introuvable"}), 404


@app.route("/loadbalancers", methods=["POST"])
def create_loadbalancer():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON manquant"}), 400

    required_fields = ["name", "ip_bind", "pass"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Champ manquant : {field}"}), 400

    loadbalancers = load_json(LOADBALANCER_FILE)

    new_id = 1
    if loadbalancers:
        new_id = max(lb["id"] for lb in loadbalancers) + 1

    new_loadbalancer = {
        "id": new_id,
        "name": data["name"],
        "ip_bind": data["ip_bind"],
        "pass": data["pass"]
    }

    loadbalancers.append(new_loadbalancer)
    save_json(LOADBALANCER_FILE, loadbalancers)

    return jsonify(new_loadbalancer), 201


@app.route("/loadbalancers/<int:loadbalancer_id>", methods=["DELETE"])
def delete_loadbalancer(loadbalancer_id):
    loadbalancers = load_json(LOADBALANCER_FILE)

    for loadbalancer in loadbalancers:
        if loadbalancer["id"] == loadbalancer_id:
            loadbalancers.remove(loadbalancer)
            save_json(LOADBALANCER_FILE, loadbalancers)
            return jsonify({"message": "Load balancer supprimé avec succès"})

    return jsonify({"error": "Load balancer introuvable"}), 404