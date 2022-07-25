import datetime
from io import BytesIO
from typing import Any, Dict, List

from flask import Blueprint
from flask import abort
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from werkzeug.datastructures import MultiDict

from app.database import connect_database
from app.models import *

bp = Blueprint(
    name="project_api",
    import_name="project_api",
    url_prefix="/projects/api"
)


@bp.route("/categories", methods=['GET'])
def get_categories():
    database = connect_database()
    return jsonify(
        database.query_all(table='category')
    )


def datetime_convert(value: Any) -> datetime.datetime:
    return datetime.datetime.strptime(value, '%Y-%m-%d')


def data_to_dict(form: MultiDict, files=None) -> Dict[str, Any]:
    data = {
        'title': form.get('title', type=str),
        'content': form.get('content', type=str),
        'created_at': form.get('created-at', type=datetime_convert),
        'category': form.get('categoryId', type=int),
        'github': form.get('github', type=str),
        'website': form.get('website', type=str)
    }

    language_key = 0
    for form_key in form.keys():
        if form_key.startswith("language"):
            language_key += form.get(form_key, type=int)
    data['language'] = language_key

    for key, value in form.items():
        if key.startswith("button-") and value is not None and value != "":
            data[f'button_{key.replace("button-", "")}'] = value

    if files is not None:
        buffer = BytesIO()
        files['image-file'].save(buffer)
        data['icon'] = buffer.getvalue()

    if 'created_at' in data and data.get('created_at', None) is None:
        data.pop('created_at')
    if 'github' in data and data.get('github', '') == '':
        data.pop('github')
    if 'website' in data and data.get('website', '') == '':
        data.pop('website')
    return data


@bp.route("/new", methods=['POST'])
def _project_new():
    if session.get('guest', True):
        return make_response(
            jsonify({
                'error': 'Forbidden',
                'message': '접근 권한이 없습니다.'
            }),
            403
        )
    form = request.form
    content_type = request.headers.get('Content-Type', None)
    if content_type.startswith("multipart/form-data"):
        files = request.files
    elif content_type.startswith("application/x-www-form-urlencoded"):
        files = None
    else:
        return abort(403)

    database = connect_database()
    project: List[Project] = database.query_all(table=Project)
    project_ids = [int(x.id) for x in project]

    minimum_id = len(project_ids) + 1
    for _id in range(1, len(project_ids)):
        if _id not in project_ids:
            minimum_id = _id
            break
    data = data_to_dict(form, files)
    data['id'] = minimum_id

    database.insert(
        table='projects',
        value=data
    )
    database.close(check_commit=True)

    return redirect(
        url_for("project.index")
    )


@bp.route("/edit/<int:project_id>", methods=['PATCH', 'POST'])
def _project_edit(project_id: int):
    if session.get('guest', True):
        return make_response(
            jsonify({
                'error': 'Forbidden',
                'message': '접근 권한이 없습니다.'
            }),
            403
        )
    form = request.form
    content_type = request.headers.get('Content-Type', None)
    if content_type.startswith("multipart/form-data"):
        files = request.files
    elif content_type.startswith("application/x-www-form-urlencoded"):
        files = None
    else:
        return abort(403)

    database = connect_database()
    data = data_to_dict(form, files)

    database.update(
        table='projects',
        key_name='id',
        key=project_id,
        value=data
    )
    database.close(check_commit=True)

    return redirect(
        url_for("project.index")
    )


@bp.route("/delete/<int:project_id>", methods=['GET', 'POST', 'DELETE'])
def _project_delete(project_id: int):
    if session.get('guest', True):
        return make_response(
            jsonify({
                'error': 'Forbidden',
                'message': '접근 권한이 없습니다.'
            }),
            403
        )

    database = connect_database()
    database.delete(
        table='projects',
        key_name='id',
        key=project_id
    )
    database.close(check_commit=True)

    return redirect(
        url_for("project.index")
    )
