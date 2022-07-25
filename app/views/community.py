
from flask import Blueprint
from flask import redirect

from app.config.config import get_config


bp = Blueprint(
    name="community",
    import_name="community",
    url_prefix="/"
)
parser = get_config()


@bp.route("/discord", methods=['GET'])
def discord():
    community_code = parser.get('Community', 'discord')
    return redirect(f"https://discord.gg/{community_code}")
