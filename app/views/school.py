from flask import Blueprint
from flask import render_template


bp = Blueprint(
    name="school",
    import_name="school",
    url_prefix="/school"
)


@bp.route("/", methods=['GET'])
def school_index():
    return "Hello World!"
