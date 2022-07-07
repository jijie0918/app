"""
profile view.

URLs include:
/users/<username>/
"""
import flask
from app import app
from app.models import get_db
from app.utils import redirect_to_login_if_session_is_not_valid


@app.route("/users/<username>/")
def show_profile(username):
    """Render profile template.

    Returns:
        Rendered template
        If not login, return login page
    """
    login_page = redirect_to_login_if_session_is_not_valid()
    if login_page is not None:
        return login_page

    conn = get_db()
    curr = conn.execute("SELECT fullname "
                        "FROM users "
                        "WHERE username = ?", (username, ))
    result = curr.fetchall()
    if len(result) == 0:
        flask.abort(404)
    context = {'fullname': result[0]['fullname'], 'username': username}

    # get posts
    curr = conn.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner= ?", (username, ))
    result = curr.fetchall()
    # sort posts according to ascending order
    context['posts'] = sorted(result, key=lambda x: x['postid'], reverse=True)

    # get follower
    curr = conn.execute(
        "SELECT COUNT(*) as count, "
        "(SELECT COUNT(*) FROM following "
        " WHERE username1 = ? AND username2 = ?) as following "
        "FROM following "
        "WHERE username2 = ?", (flask.session['logname'], username, username))
    result = curr.fetchall()
    context['follower'] = result[0]['count']
    context['logname_follow_username'] = (result[0]['following'] == 1)

    # get following
    curr = conn.execute(
        "SELECT COUNT(*) as count "
        "FROM following "
        "WHERE username1 = ?", (username, ))
    result = curr.fetchall()
    context['following'] = result[0]['count']

    return flask.render_template("profile.html", **context)
