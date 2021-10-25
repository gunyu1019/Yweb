from flask import Blueprint
from flask import render_template


bp = Blueprint(
    name="short",
    import_name="short",
    url_prefix="/s"
)


@bp.route("/", methods=['GET'])
def short_index():
    return "Hello World!"


@bp.route("/<link>", methods=['GET'])
def short(link):
    return "Hello World!"
