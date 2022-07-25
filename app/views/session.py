from flask import Blueprint
from flask import session
from flask import redirect
from flask import request
from flask import make_response
from flask import jsonify
from flask import url_for
from urllib.error import HTTPError

from app.config.config import get_config
from app.microsoft import Microsoft
from app.utils import from_json


bp = Blueprint(
    name="session",
    import_name="session",
    url_prefix="/session"
)
parser = get_config()
client = Microsoft(
    client_id=parser.get("microsoft-oauth2", "client_id"),
    client_secret=parser.get("microsoft-oauth2", "client_secret")
)
scope = parser.get("microsoft-oauth2", "scope").split()


@bp.route("/logout", methods=['GET'])
def logout():
    for key in list(session.keys()):
        del session[key]

    return redirect(
        url_for("index.index")
    )


@bp.route("/login", methods=['GET'])
def login():
    return redirect(
        client.authorize(
            redirect_uri="https://" + request.host + "/session/callback",
            scope=scope
        )
    )


@bp.route("/callback", methods=['GET'])
def callback():
    code = request.args.get("code", None)
    if code is None:
        return make_response("wrong approach", 403)

    try:
        access_token = client.generate_access_token(
            code=code,
            redirect_uri="https://" + request.host + "/session/callback",
            scope=scope
        )
    except HTTPError as error:
        result = from_json(error.read().decode())
        return make_response(jsonify({
            "title": result.get("error"),
            "message": result.get("error_description")
        }), error.code)
    if access_token.token == "":
        return redirect(
            url_for("session.login")
        )

    user = client.get_user(access_token)
    # return "Are you Moderator?: {0}".format(check_permission(access_token))
    session['access_token'] = access_token.to_dict()
    session['user'] = user.id
    if user.id != parser.get('owner', 'microsoft-id'):
        session['guest'] = True

        return redirect(
            url_for("index.index")
        )
    session['guest'] = False
    return redirect(
        url_for("index.index")
    )
