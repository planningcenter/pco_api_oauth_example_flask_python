from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
import json
import os
import pprint

app = Flask(__name__)
app.secret_key = os.urandom(24)

client_id = os.environ["OAUTH_APP_ID"]
client_secret = os.environ["OAUTH_SECRET"]
domain = os.environ.get("DOMAIN", "http://localhost:5000")
api_url = "https://api.planningcenteronline.com"
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
        people = pco.get(f"{api_url}/people/v2/people").json()
        people_formatted = pprint.PrettyPrinter(indent=2).pformat(people)
        return f"<a href='/auth/logout'>log out</a><br><pre>%s</pre>" % people_formatted
    else:
        return f"<a href='/auth'>authenticate with API</a>"

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
