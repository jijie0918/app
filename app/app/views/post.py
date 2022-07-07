"""
post view.

URLs include:
/posts/<int:postid>/
"""
import flask
from app import app
from app.get_context import get_post_context
from app.utils import redirect_to_login_if_session_is_not_valid


@app.route("/posts/<int:postid>/")
def show_post(postid):
    """Render post template.

    Returns:
        Rendered template
        If not login, return login page
    """
    login_page = redirect_to_login_if_session_is_not_valid()
    if login_page is not None:
        return login_page

    context = get_post_context(postid, logname=flask.session['logname'])
    return flask.render_template("post.html", **context)
