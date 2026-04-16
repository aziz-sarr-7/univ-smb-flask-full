from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

API_URL = "http://127.0.0.1:5000"


@app.route("/")
def home():
    return """
    <h1>Accueil OK</h1>
    <p><a href='/webservers'>Voir les webservers</a></p>
    <p><a href='/reverseproxies'>Voir les reverse proxies</a></p>
    <p><a href='/loadbalancers'>Voir les load balancers</a></p>
    """


# --------------------
# WEBSERVERS
# --------------------

@app.route("/webservers")
def webservers_list():
    response = requests.get(f"{API_URL}/webservers")
    webservers = response.json()
    return render_template("webservers_list.html", webservers=webservers)


@app.route("/webservers/<int:webserver_id>")
def webserver_detail(webserver_id):
    response = requests.get(f"{API_URL}/webservers/{webserver_id}")
    webserver = response.json()
    return render_template("webserver_detail.html", webserver=webserver)


@app.route("/webservers/add", methods=["GET", "POST"])
def add_webserver():
    if request.method == "POST":
        data = {
            "server_name": request.form["server_name"],
            "listen": int(request.form["listen"]),
            "root": request.form["root"]
        }
        requests.post(f"{API_URL}/webservers", json=data)
        return redirect("/webservers")

    return render_template("webserver_add.html")


@app.route("/webservers/delete/<int:webserver_id>", methods=["POST"])
def delete_webserver(webserver_id):
    requests.delete(f"{API_URL}/webservers/{webserver_id}")
    return redirect("/webservers")


# --------------------
# REVERSE PROXIES
# --------------------

@app.route("/reverseproxies")
def reverseproxies_list():
    response = requests.get(f"{API_URL}/reverseproxies")
    reverseproxies = response.json()
    return render_template("reverseproxies_list.html", reverseproxies=reverseproxies)


@app.route("/reverseproxies/<int:reverseproxy_id>")
def reverseproxy_detail(reverseproxy_id):
    response = requests.get(f"{API_URL}/reverseproxies/{reverseproxy_id}")
    reverseproxy = response.json()
    return render_template("reverseproxy_detail.html", reverseproxy=reverseproxy)


@app.route("/reverseproxies/add", methods=["GET", "POST"])
def add_reverseproxy():
    if request.method == "POST":
        data = {
            "server_name": request.form["server_name"],
            "listen": int(request.form["listen"]),
            "proxy_pass": request.form["proxy_pass"]
        }
        requests.post(f"{API_URL}/reverseproxies", json=data)
        return redirect("/reverseproxies")

    return render_template("reverseproxy_add.html")


@app.route("/reverseproxies/delete/<int:reverseproxy_id>", methods=["POST"])
def delete_reverseproxy(reverseproxy_id):
    requests.delete(f"{API_URL}/reverseproxies/{reverseproxy_id}")
    return redirect("/reverseproxies")
@app.route("/loadbalancers")
def loadbalancers_list():
    response = requests.get(f"{API_URL}/loadbalancers")
    loadbalancers = response.json()
    return render_template("loadbalancers_list.html", loadbalancers=loadbalancers)


@app.route("/loadbalancers/<int:loadbalancer_id>")
def loadbalancer_detail(loadbalancer_id):
    response = requests.get(f"{API_URL}/loadbalancers/{loadbalancer_id}")
    loadbalancer = response.json()
    return render_template("loadbalancer_detail.html", loadbalancer=loadbalancer)


@app.route("/loadbalancers/add", methods=["GET", "POST"])
def add_loadbalancer():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "ip_bind": request.form["ip_bind"],
            "pass": request.form["pass"]
        }
        requests.post(f"{API_URL}/loadbalancers", json=data)
        return redirect("/loadbalancers")

    return render_template("loadbalancer_add.html")


@app.route("/loadbalancers/delete/<int:loadbalancer_id>", methods=["POST"])
def delete_loadbalancer(loadbalancer_id):
    requests.delete(f"{API_URL}/loadbalancers/{loadbalancer_id}")
    return redirect("/loadbalancers")