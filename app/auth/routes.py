import requests

import json

from flask_login import logout_user, login_required

from flask_login import login_user

from flask_babel import _

from oauthlib.oauth2 import WebApplicationClient

from flask import(
    redirect, 
    url_for, 
    request, 
    session, 
    current_app
    )

from app.auth.auth_functions import get_google_provider_cfg

from app.auth import bp

from app.models import User


@bp.route('/login')
def login():
    """This initiates the google log in process."""
    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg[
        "authorization_endpoint"
        ]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        prompt='consent'
    )
    return redirect(request_uri)


@bp.route("/login/callback")
def callback():
    """
    
    This deals with the Google API token for user 
    authentification.
    """
    
    client = WebApplicationClient(
        current_app.config['GOOGLE_CLIENT_ID']
        )
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
        )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(
            current_app.config['GOOGLE_CLIENT_ID'], 
            current_app.config['GOOGLE_CLIENT_SECRET']
            ),
        )
    client.parse_request_body_response(
        json.dumps(token_response.json())
        )
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(
        uri, 
        headers=headers, 
        data=body
        )
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
        if User.query.filter_by(email=users_email).first():
            user = User.query.filter_by(email=users_email).first()
            if user is None or not user.check_password(unique_id):
                return redirect(url_for('shop.index'))
            login_user(user, remember=False)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('shop.index')
            return redirect(next_page)
        else:
            user = User(username=users_name, email=users_email)
            user.set_password(unique_id)
            db.session.add(user)
            db.session.commit()
    else:
        return _("User email not available or not verified by Google."), 400
    return redirect(url_for("shop.index"))


@bp.route('/logout')
@login_required
def logout():
    """This logs a user out."""
    logout_user()
    return redirect(url_for('shop.clear_session'))