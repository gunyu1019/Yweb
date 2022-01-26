from flask import Blueprint
from flask import render_template


bp = Blueprint(
    name="index",
    import_name="index",
    url_prefix="/"
)


@bp.route("/", methods=['GET'])
def index():
    return render_template("pages/index.html")
