"""helper function for insta485.views."""
import uuid
import hashlib
import pathlib
import flask
from app import app
from app.api.exceptions import ForbiddenException
from app.models import get_db


def verify_password(pw_local, pw_remote):
    """Test if the plain local password matches encrypted remote password.

    Args:
        pw_local (str): plain local password
        pw_remote (str): encrypted remote password

    Returns:
        bool: password matches or not
    """
    [alg, salt, pw_hash_remote] = pw_remote.split("$")
    hash_obj = hashlib.new(alg)
    pw_salted_local = salt + pw_local
    hash_obj.update(pw_salted_local.encode('utf-8'))
    pw_hash_local = hash_obj.hexdigest()
    return pw_hash_local == pw_hash_remote


def encrypt_password(password, alg="sha512"):
    """Encrypt password.

    Args:
        pw (str): plain password
        alg (str, optional): algorithm to encode password.
        Defaults to "sha512".

    Returns:
        str: encrypted password
    """
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(alg)
    pw_salted = salt + password
    hash_obj.update(pw_salted.encode('utf-8'))
    pw_hash = hash_obj.hexdigest()
    password_db_string = "$".join([alg, salt, pw_hash])
    return password_db_string


def save_file_and_get_path(file_obj):
    """Save new file.

    Return:
        new file path
    """
    filename = file_obj.filename

    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"

    path = app.config["UPLOAD_FOLDER"] / uuid_basename
    file_obj.save(path)
    return uuid_basename


def remove_file(filename):
    """Remove file from original path."""
    file_path = pathlib.Path(app.config["UPLOAD_FOLDER"] / filename)
    file_path.unlink()


def redirect_to_login_if_session_is_not_valid():
    """Connect to database and verify if log name is valid.

    Return:
        Response: redirect destination
    """
    redirect_page = None
    if "logname" not in flask.session:
        redirect_page = flask.redirect(flask.url_for("login"))
        return redirect_page

    # Connect to database
    connection = get_db()

    # check if the logname still exits in database
    cur = connection.execute(
        "SELECT COUNT(*) as count "
        "FROM users "
        "WHERE username = ?", (flask.session['logname'], ))

    count = cur.fetchone()['count']
    if count == 0:
        flask.session.clear()
        redirect_page = flask.redirect(flask.url_for('login'))
    return redirect_page


def authen_rest_api_and_get_logname():
    """Check authetication for Rest API."""
    logname = None
    if (flask.request.authorization is not None
            and 'username' in flask.request.authorization
            and 'password' in flask.request.authorization):
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        authenticate(username, password, from_rest_api=True)
        logname = username
    elif 'logname' in flask.session:
        logname = flask.session['logname']
    else:
        raise ForbiddenException
    return logname


def authenticate(username, password, from_rest_api=False):
    """Check if username match password."""
    # set connection and authenticate the user
    conn = get_db()
    cur = conn.execute(
        "SELECT username, password "
        "FROM users "
        "WHERE username = ?", (username, ))
    user = cur.fetchall()
    if len(user) != 1:
        if from_rest_api:
            raise ForbiddenException
        flask.abort(403)
    if not verify_password(password, user[0]['password']):
        if from_rest_api:
            raise ForbiddenException
        flask.abort(403)
