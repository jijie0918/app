"""
index (main) view.

URLs include:
/
"""
import flask
from app import app
from app.utils import redirect_to_login_if_session_is_not_valid


@app.route('/')
def show_index():
    """Render index template.

    Returns:
        Rendered template
        If not login, return login page
    """
    login_page = redirect_to_login_if_session_is_not_valid()
    if login_page is not None:
        return login_page
    return flask.render_template("index.html")
