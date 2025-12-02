from flask import Flask, request, jsonify
import requests
import time
import uuid

app = Flask(__name__)

PINS = {}

def build_google_auth_url(client_id, redirect_uri):
    scope = (
        "https://www.googleapis.com/auth/drive "
        "https://www.googleapis.com/auth/drive.file "
        "https://www.googleapis.com/auth/userinfo.profile"
    )

    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        "&access_type=offline"
        "&prompt=consent"
        "&client_id=" + client_id +
        "&redirect_uri=" + redirect_uri +
        "&scope=" + requests.utils.quote(scope)
    )


@app.route("/pin", methods=["POST"])
def create_pin():
    provider = request.form.get("provider")
    client_id = request.form.get("client_id")
    redirect_uri = request.form.get("redirect_uri", "http://localhost")

    pin = str(uuid.uuid4())[:8]

    PINS[pin] = {
        "provider": provider,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "created": time.time()
    }

    return jsonify({
        "pin": pin,
        "password": "",
        "verification_url": build_google_auth_url(client_id, redirect_uri)
    })


@app.route("/pin/<pin>", methods=["GET"])
def exchange_pin(pin):
    if pin not in PINS:
        return jsonify({"error": "invalid_pin"}), 404

    code = request.headers.get("authorization", "")
    if code.startswith("Basic :"):
        code = code.replace("Basic :", "").strip()

    client_secret = request.args.get("client_secret")
    if not client_secret:
        return jsonify({"error": "missing_client_secret"}), 400

    client_id = PINS[pin]["client_id"]
    redirect_uri = PINS[pin]["redirect_uri"]

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    r = requests.post("https://oauth2.googleapis.com/token", data=data)

    if r.status_code != 200:
        return r.text, r.status_code

    resp = r.json()
    resp["date"] = time.time()
    return jsonify(resp)


@app.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = request.form.get("refresh_token")
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")

    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }

    r = requests.post("https://oauth2.googleapis.com/token", data=data)
    resp = r.json()
    resp["date"] = time.time()
    return jsonify(resp)


@app.route("/")
def home():
    return "Google Drive OAuth Server OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)