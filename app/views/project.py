from flask import Blueprint
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from typing import List

from app.database import connect_database
from app.models import *


bp = Blueprint(
    name="project",
    import_name="project",
    url_prefix="/projects"
)


@bp.route("/", methods=['GET'])
def index():
    query = request.args.get('query')
    database = connect_database()
    categories: List[Category] = database.query_all(table=Category)
    languages: List[Language] = database.query_all(table=Language)
    if query is None:
        project: List[Project] = database.query_all(
            table=Project
        )
    else:
        project: List[Project] = database.query_all(
            table=Project,
            key_name='title',
            key=query,
            similar=True
        )

    params_category = request.args.get('category')
    params_language = request.args.get('language', '').split(',')
    is_admin = not session.get('guest', True)
    database.close()
    return render_template(
        "pages/project.html",
        is_admin=is_admin,
        categories=categories,
        languages=languages,
        projects=project,
        main_category=params_category,
        main_language=params_language
    )


@bp.route("/<int:project_id>", methods=['GET'])
def detail(project_id: int):
    database = connect_database()

    project: Project = database.query(table=Project, key_name='id', key=project_id)
    category: Category = database.query(table=Category, key_name='id', key=project.category)
    languages: List[Language] = database.query_all(table=Language)
    database.close()

    is_admin = not session.get('guest', True)
    return render_template(
        "pages/project_detail.html",
        is_admin=is_admin,
        category=category,
        languages=languages,
        project=project
    )


@bp.route("/<int:project_id>/edit", methods=['GET'])
def project_edit(project_id: int):
    database = connect_database()

    project: Project = database.query(table=Project, key_name='id', key=project_id)
    categories: List[Category] = database.query_all(table=Category)
    languages: List[Language] = database.query_all(table=Language)
    database.close()

    is_admin = not session.get('guest', True)
    return render_template(
        "pages/editor.html",
        is_admin=is_admin,
        categories=categories,
        languages=languages,
        redirect_url=url_for('project_api._project_edit', project_id=project.id),
        default_language=project.language,
        default_content=project.content,
        default_title=project.title,
        default_category=project.category,
        default_datetime=project.created_at.strftime('%Y-%m-%d'),
        default_github=project.github if project.github is not None else '',
        default_website=project.website if project.website is not None else '',
        default_button=project.button,
        default_image=f"data:image/png;base64,{project.icon_convert}"
    )


@bp.route("/new", methods=['GET'])
def project_new():
    database = connect_database()
    categories: List[Category] = database.query_all(table=Category)
    languages: List[Language] = database.query_all(table=Language)
    database.close()

    is_admin = not session.get('guest', True)
    return render_template(
        "pages/editor.html",
        is_admin=is_admin,
        categories=categories,
        languages=languages
    )
