from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, render_template, session, url_for
import json
import os
import pprint

app = Flask(__name__)
app.secret_key = os.urandom(24)

client_id = os.environ["OAUTH_APP_ID"]
client_secret = os.environ["OAUTH_SECRET"]
domain = os.environ.get("DOMAIN", "http://localhost:5000")
api_url = os.environ.get("API_URL", "https://api.planningcenteronline.com")
token_url = f"{api_url}/oauth/token"

def token_updater(token):
    session["oauth_token"] = token

pco = OAuth2Session(client_id,
        scope="people services",
        redirect_uri=f"{domain}/auth/complete",
        auto_refresh_kwargs={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        auto_refresh_url=token_url,
        token_updater=token_updater)

@app.route("/")
def index():
    if "oauth_token" in session:
        response = pco.get(f"{api_url}/people/v2/people").json()
        formatted_response = pprint.PrettyPrinter(indent=2).pformat(response)
        return render_template("index.html", logged_in=True, people=response['data'], formatted_response=formatted_response)
    else:
        return render_template("login.html")

@app.route("/auth")
def auth():
    authorization_url, state = pco.authorization_url(f"{api_url}/oauth/authorize")
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route("/auth/complete", methods=["GET"])
def callback():
    token = pco.fetch_token(token_url, client_secret=client_secret,
                            authorization_response=request.url)
    session["oauth_token"] = token
    return redirect("/")

@app.route("/auth/logout")
def logout():
    pco.post(f"{api_url}/oauth/revoke", data={"token": session["oauth_token"]})
    del session["oauth_token"]
    return redirect("/")
