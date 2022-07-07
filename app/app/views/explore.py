"""
explore view.

URLs include:
/explore/
"""
import flask
from app import app
from app.models import get_db
from app.utils import redirect_to_login_if_session_is_not_valid


@app.route("/explore/", methods=["GET", "POST"])
def explore():
    """Render explore template.

    Returns:
        Response: rendered template
        If not login, return login page
    """
    login_page = redirect_to_login_if_session_is_not_valid()
    if login_page is not None:
        return login_page

    connection = get_db()
    explore_query_result = connection.execute(
        "SELECT username, filename as profile_filename "
        "FROM users "
        "WHERE users.username NOT IN "
        "(SELECT username2 FROM following WHERE username1 = ?) "
        "AND users.username != ? ",
        (flask.session['logname'], flask.session['logname']))
    not_following = explore_query_result.fetchall()
    context = {"not_following": not_following}

    return flask.render_template("explore.html", **context)
