from flask import Flask, render_template, request, redirect, flash, Response, session
import requests

app = Flask(__name__)
app.secret_key = "tp-secret-key"

API_URL = "http://127.0.0.1:5000"


def require_login():
    if not session.get("logged_in"):
        return redirect("/login")
    return None


def generate_webserver_config(webserver):
    return f"""server {{
    listen {webserver['listen']};
    server_name {webserver['server_name']};
    root {webserver['root']};
}}
"""


def generate_reverseproxy_config(reverseproxy):
    return f"""server {{
    listen {reverseproxy['listen']};
    server_name {reverseproxy['server_name']};

    location / {{
        proxy_pass {reverseproxy['proxy_pass']};
    }}
}}
"""


def generate_loadbalancer_config(loadbalancer):
    upstream_name = loadbalancer["name"].replace(" ", "_")
    backend = loadbalancer["pass"].replace("http://", "").replace("https://", "")

    return f"""upstream {upstream_name} {{
    server {backend};
}}

server {{
    listen 80;
    server_name {loadbalancer['ip_bind']};

    location / {{
        proxy_pass {loadbalancer['pass']};
    }}
}}
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect("/")
        else:
            flash("Identifiants invalides.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def home():
    auth = require_login()
    if auth:
        return auth

    return """
    <h1>Web Configurator</h1>
    <p><a href='/webservers'>Voir les webservers</a></p>
    <p><a href='/reverseproxies'>Voir les reverse proxies</a></p>
    <p><a href='/loadbalancers'>Voir les load balancers</a></p>
    <p><a href='/logout'>Se déconnecter</a></p>
    """


# --------------------
# WEBSERVERS
# --------------------

@app.route("/webservers")
def webservers_list():
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/webservers")
    webservers = response.json()
    return render_template("webservers_list.html", webservers=webservers)


@app.route("/webservers/<int:webserver_id>")
def webserver_detail(webserver_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/webservers/{webserver_id}")
    if response.status_code != 200:
        return "Serveur web introuvable", 404

    webserver = response.json()
    return render_template("webserver_detail.html", webserver=webserver)


@app.route("/webservers/add", methods=["GET", "POST"])
def add_webserver():
    auth = require_login()
    if auth:
        return auth

    if request.method == "POST":
        server_name = request.form["server_name"].strip()
        listen = request.form["listen"].strip()
        root = request.form["root"].strip()

        if not server_name:
            flash("Le nom du serveur est obligatoire.")
            return render_template("webserver_add.html")

        if not listen.isdigit() or int(listen) <= 0 or int(listen) > 65535:
            flash("Le port doit être un nombre entre 1 et 65535.")
            return render_template("webserver_add.html")

        if not root:
            flash("Le champ root est obligatoire.")
            return render_template("webserver_add.html")

        data = {
            "server_name": server_name,
            "listen": int(listen),
            "root": root
        }

        requests.post(f"{API_URL}/webservers", json=data)
        return redirect("/webservers")

    return render_template("webserver_add.html")


@app.route("/webservers/delete/<int:webserver_id>", methods=["POST"])
def delete_webserver(webserver_id):
    auth = require_login()
    if auth:
        return auth

    requests.delete(f"{API_URL}/webservers/{webserver_id}")
    return redirect("/webservers")


@app.route("/webservers/<int:webserver_id>/download")
def download_webserver_config(webserver_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/webservers/{webserver_id}")
    if response.status_code != 200:
        return "Serveur web introuvable", 404

    webserver = response.json()
    config = generate_webserver_config(webserver)

    return Response(
        config,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=webserver_{webserver_id}.conf"
        }
    )


@app.route("/webservers/<int:webserver_id>/prepare")
def prepare_webserver(webserver_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/webservers/{webserver_id}")
    if response.status_code != 200:
        return "Serveur web introuvable", 404

    webserver = response.json()
    config = generate_webserver_config(webserver)
    filename = f"webserver_{webserver_id}.conf"
    target_path = f"/etc/nginx/sites-available/{filename}"

    commands = [
        f"sudo cp {filename} {target_path}",
        f"sudo ln -s {target_path} /etc/nginx/sites-enabled/{filename}",
        "sudo nginx -t",
        "sudo systemctl reload nginx"
    ]

    return render_template(
        "prepare_config.html",
        title="Préparation du serveur web",
        config=config,
        filename=filename,
        target_path=target_path,
        commands=commands
    )


# --------------------
# REVERSE PROXIES
# --------------------

@app.route("/reverseproxies")
def reverseproxies_list():
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/reverseproxies")
    reverseproxies = response.json()
    return render_template("reverseproxies_list.html", reverseproxies=reverseproxies)


@app.route("/reverseproxies/<int:reverseproxy_id>")
def reverseproxy_detail(reverseproxy_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/reverseproxies/{reverseproxy_id}")
    if response.status_code != 200:
        return "Reverse proxy introuvable", 404

    reverseproxy = response.json()
    return render_template("reverseproxy_detail.html", reverseproxy=reverseproxy)


@app.route("/reverseproxies/add", methods=["GET", "POST"])
def add_reverseproxy():
    auth = require_login()
    if auth:
        return auth

    if request.method == "POST":
        server_name = request.form["server_name"].strip()
        listen = request.form["listen"].strip()
        proxy_pass = request.form["proxy_pass"].strip()

        if not server_name:
            flash("Le nom du serveur est obligatoire.")
            return render_template("reverseproxy_add.html")

        if not listen.isdigit() or int(listen) <= 0 or int(listen) > 65535:
            flash("Le port doit être un nombre entre 1 et 65535.")
            return render_template("reverseproxy_add.html")

        if not proxy_pass:
            flash("Le champ proxy_pass est obligatoire.")
            return render_template("reverseproxy_add.html")

        data = {
            "server_name": server_name,
            "listen": int(listen),
            "proxy_pass": proxy_pass
        }

        requests.post(f"{API_URL}/reverseproxies", json=data)
        return redirect("/reverseproxies")

    return render_template("reverseproxy_add.html")


@app.route("/reverseproxies/delete/<int:reverseproxy_id>", methods=["POST"])
def delete_reverseproxy(reverseproxy_id):
    auth = require_login()
    if auth:
        return auth

    requests.delete(f"{API_URL}/reverseproxies/{reverseproxy_id}")
    return redirect("/reverseproxies")


@app.route("/reverseproxies/<int:reverseproxy_id>/download")
def download_reverseproxy_config(reverseproxy_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/reverseproxies/{reverseproxy_id}")
    if response.status_code != 200:
        return "Reverse proxy introuvable", 404

    reverseproxy = response.json()
    config = generate_reverseproxy_config(reverseproxy)

    return Response(
        config,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=reverseproxy_{reverseproxy_id}.conf"
        }
    )


@app.route("/reverseproxies/<int:reverseproxy_id>/prepare")
def prepare_reverseproxy(reverseproxy_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/reverseproxies/{reverseproxy_id}")
    if response.status_code != 200:
        return "Reverse proxy introuvable", 404

    reverseproxy = response.json()
    config = generate_reverseproxy_config(reverseproxy)
    filename = f"reverseproxy_{reverseproxy_id}.conf"
    target_path = f"/etc/nginx/sites-available/{filename}"

    commands = [
        f"sudo cp {filename} {target_path}",
        f"sudo ln -s {target_path} /etc/nginx/sites-enabled/{filename}",
        "sudo nginx -t",
        "sudo systemctl reload nginx"
    ]

    return render_template(
        "prepare_config.html",
        title="Préparation du reverse proxy",
        config=config,
        filename=filename,
        target_path=target_path,
        commands=commands
    )


# --------------------
# LOAD BALANCERS
# --------------------

@app.route("/loadbalancers")
def loadbalancers_list():
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/loadbalancers")
    loadbalancers = response.json()
    return render_template("loadbalancers_list.html", loadbalancers=loadbalancers)


@app.route("/loadbalancers/<int:loadbalancer_id>")
def loadbalancer_detail(loadbalancer_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/loadbalancers/{loadbalancer_id}")
    if response.status_code != 200:
        return "Load balancer introuvable", 404

    loadbalancer = response.json()
    return render_template("loadbalancer_detail.html", loadbalancer=loadbalancer)


@app.route("/loadbalancers/add", methods=["GET", "POST"])
def add_loadbalancer():
    auth = require_login()
    if auth:
        return auth

    if request.method == "POST":
        name = request.form["name"].strip()
        ip_bind = request.form["ip_bind"].strip()
        passed_value = request.form["pass"].strip()

        if not name:
            flash("Le nom est obligatoire.")
            return render_template("loadbalancer_add.html")

        if not ip_bind:
            flash("Le champ ip_bind est obligatoire.")
            return render_template("loadbalancer_add.html")

        if not passed_value:
            flash("Le champ pass est obligatoire.")
            return render_template("loadbalancer_add.html")

        data = {
            "name": name,
            "ip_bind": ip_bind,
            "pass": passed_value
        }

        requests.post(f"{API_URL}/loadbalancers", json=data)
        return redirect("/loadbalancers")

    return render_template("loadbalancer_add.html")


@app.route("/loadbalancers/delete/<int:loadbalancer_id>", methods=["POST"])
def delete_loadbalancer(loadbalancer_id):
    auth = require_login()
    if auth:
        return auth

    requests.delete(f"{API_URL}/loadbalancers/{loadbalancer_id}")
    return redirect("/loadbalancers")


@app.route("/loadbalancers/<int:loadbalancer_id>/download")
def download_loadbalancer_config(loadbalancer_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/loadbalancers/{loadbalancer_id}")
    if response.status_code != 200:
        return "Load balancer introuvable", 404

    loadbalancer = response.json()
    config = generate_loadbalancer_config(loadbalancer)

    return Response(
        config,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=loadbalancer_{loadbalancer_id}.conf"
        }
    )


@app.route("/loadbalancers/<int:loadbalancer_id>/prepare")
def prepare_loadbalancer(loadbalancer_id):
    auth = require_login()
    if auth:
        return auth

    response = requests.get(f"{API_URL}/loadbalancers/{loadbalancer_id}")
    if response.status_code != 200:
        return "Load balancer introuvable", 404

    loadbalancer = response.json()
    config = generate_loadbalancer_config(loadbalancer)
    filename = f"loadbalancer_{loadbalancer_id}.conf"
    target_path = f"/etc/nginx/sites-available/{filename}"

    commands = [
        f"sudo cp {filename} {target_path}",
        f"sudo ln -s {target_path} /etc/nginx/sites-enabled/{filename}",
        "sudo nginx -t",
        "sudo systemctl reload nginx"
    ]

    return render_template(
        "prepare_config.html",
        title="Préparation du load balancer",
        config=config,
        filename=filename,
        target_path=target_path,
        commands=commands
    )