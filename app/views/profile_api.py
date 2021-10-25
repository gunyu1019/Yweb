from flask import Blueprint
from flask import make_response, jsonify
from requests import request
from app.config.config import get_config


bp = Blueprint(
    name="profile_api",
    import_name="profile_api",
    url_prefix="/api"
)


@bp.route("/repositories", methods=['GET'])
def repositories():
    parser = get_config()
    if not parser.has_option("token", "github"):
        return make_response(
            jsonify({
                "CODE": 401,
                "MESSAGE": "GitHub token is missing."
            }),
            401
        )

    params = {
        "per_page": "100",
        "affiliation": "owner",
        "page": "1"
    }
    headers = {
        "Authorization": "token {0}".format(
            parser.get("token", "github")
        )
    }
    response1 = request(
        "GET",
        "https://api.github.com/user/repos",
        params=params,
        headers=headers
    )
    repos = response1.json()
    result = {}
    for repo in repos:
        name = repo["name"]
        if repo["fork"]:
            continue
        response2 = request(
            "GET",
            "https://api.github.com/repos/gunyu1019/{name}/languages".format(name=name),
            headers=headers)
        language_result = response2.json()
        for key in language_result:
            if key in result.keys():
                result[key] += language_result[key]
            else:
                result[key] = language_result[key]

    return make_response(
        jsonify(result),
        200
    )


@bp.route("/projects", methods=['GET'])
def projects():
    return "Hello World!"


@bp.route("/teams", methods=['GET'])
def teams():
    return "Hello World!"
