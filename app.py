from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, render_template, session, url_for
import json
import os
import pprint
import jwt

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
        scope="openid email profile people services",
        redirect_uri=f"{domain}/auth/complete",
        auto_refresh_kwargs={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        auto_refresh_url=token_url,
        token_updater=token_updater)

def fetch_user_info():
    # if the id_token is not present then no openid scopes were requested
    if "id_token" not in session.get("oauth_token", {}):
        return None
    userinfo = pco.get(f"{api_url}/oauth/userinfo").json()
    return userinfo

def parse_id_token(id_token):
    try:
        # Basic JWT decoding without signature verification for demo purposes only.
        #
        # NOTE: In production, you should verify the JWT signature using the JWK from the
        # JWKS endpoint ({API_URL}/oauth/discovery/keys).
        #
        # This verification will happen automatically if using an authentication
        # package like `pyoidc` or `oidc-client`. Otherwise a package like `pyjwt`
        # can be used to manually build the public key from the JWK hash to pass into
        # `jwt.decode`.
        id_token_claims = jwt.decode(id_token, options={"verify_signature": False})
        return id_token_claims
    except Exception as e:
        print(f"Failed to decode ID token: {e}")
        return None

@app.route("/")
def index():
    if "oauth_token" in session:
        return redirect("/people")
    else:
        return render_template("login.html")

@app.route("/auth")
def auth():
    authorization_url, state = pco.authorization_url(f"{api_url}/oauth/authorize", prompt="select_account")
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route("/auth/complete", methods=["GET"])
def callback():
    token = pco.fetch_token(token_url, client_secret=client_secret,
                            authorization_response=request.url)
    session["oauth_token"] = token

    if 'id_token' in token:
        session["current_user"] = {
            "name": fetch_user_info().get("name", ""),
            "claims": parse_id_token(token['id_token'])
        }
    return redirect("/")

@app.route("/people")
def people():
    if "oauth_token" not in session:
        return redirect("/")

    response = pco.get(f"{api_url}/people/v2/people").json()
    formatted_response = pprint.PrettyPrinter(indent=2).pformat(response)
    return render_template("people.html", logged_in=True, people=response['data'], formatted_response=formatted_response)
@app.route("/auth/logout")
def logout():
    pco.post(f"{api_url}/oauth/revoke", data={"token": session["oauth_token"]})
    if "oauth_token" in session:
        del session["oauth_token"]
    if "current_user" in session:
        del session["current_user"]
    return redirect("/")
