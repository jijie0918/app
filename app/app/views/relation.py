"""
index (main) view.

URLs include:
/users/<user_url_slug>/followings/
/users/<user_url_slug>/followers/
"""
import flask
from app import app
from app.models import get_db
from app.utils import redirect_to_login_if_session_is_not_valid


def show_relation(username, relation="following"):
    """Render template for following or follower."""
    login_page = redirect_to_login_if_session_is_not_valid()
    if login_page is not None:
        return login_page

    connection = get_db()
    # Check if exist
    cur = connection.execute(
        "SELECT COUNT(*) as count "
        "FROM users "
        "WHERE username = ? ", (username, ))
    num = cur.fetchall()

    # username does not exist in db
    if num[0]['count'] == 0:
        flask.abort(404)

    # Get connection from db
    if relation == "follower":
        cur = connection.execute(
            "SELECT f.username1 as username, u.filename as profile_filename "
            "FROM following f "
            "JOIN users u "
            "ON u.username = f.username1 "
            "WHERE f.username2 = ? ", (username, ))
    elif relation == "following":
        cur = connection.execute(
            "SELECT f.username2 as username, u.filename as profile_filename "
            "FROM following f "
            "JOIN users u "
            "ON u.username = f.username2 "
            "WHERE f.username1 = ? ", (username, ))

    # Query database
    query_result = cur.fetchall()
    for person in query_result:
        cur = connection.execute(
            "SELECT COUNT(*) as count "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (flask.session['logname'], person['username']))
        result = cur.fetchall()
        person['logname_follow_username'] = result[0]['count'] != 0

    # Add database info to context
    context = {relation: query_result, "username": username}

    return flask.render_template(f"{relation}.html", **context)


@app.route('/users/<username>/following/')
def show_following(username):
    """Render following template."""
    return show_relation(username, "following")


@app.route('/users/<username>/followers/')
def show_follower(username):
    """Render follower template."""
    return show_relation(username, "follower")
