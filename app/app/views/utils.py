"""Helper function for view."""
import flask
from app import app
from app.utils import verify_password, encrypt_password, authenticate
from app.utils import save_file_and_get_path, remove_file
from app.models import get_db



@app.route("/uploads/<path:name>")
def download_file(name):
    """Download file from upload folder.

    Args:
        name (str): the name of request file

    Returns:
        Response: downloaded file
    """
    if "logname" not in flask.session:
        flask.abort(403)

    return flask.send_from_directory(app.config['UPLOAD_FOLDER'],
                                     name)


@app.route("/comments/", methods=["POST"])
def comment_handler():
    """Create or delete a comments and direct to URL.

    Returns:
        Returns:
        Response: redirecte destination
    """
    if "logname" not in flask.session:
        flask.abort(403)

    if 'target' not in flask.request.args:
        redirect_link = flask.url_for('show_index')
    else:
        redirect_link = flask.request.args['target']

    conn = get_db()
    operation = flask.request.form['operation']
    if operation == "create":
        postid = flask.request.form['postid']
        text = flask.request.form.get('text')
        # ! maybe empty string instead of None
        if text is None or text == '':
            flask.abort(400)
        cur = conn.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?) ", (flask.session['logname'], postid, text))

    if operation == "delete":
        commentid = flask.request.form['commentid']
        cur = conn.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid = ? ", (commentid, ))
        comment = cur.fetchall()
        if flask.session["logname"] != comment[0]['owner']:
            flask.abort(403)
        conn.execute("DELETE FROM comments "
                     "WHERE commentid = ? ", (commentid, ))

    return flask.redirect(redirect_link)


@app.route("/likes/", methods=["POST"])
def like_handler():
    """Create like or delete like and redirect to URL.

    Returns:
        Response: redirecte destination
    """
    if "logname" not in flask.session:
        flask.abort(403)

    if 'target' not in flask.request.args:
        redirect_link = flask.url_for('show_index')
    else:
        redirect_link = flask.request.args['target']

    conn = get_db()
    postid = flask.request.form.get('postid')
    operation = flask.request.form['operation']
    cur = conn.execute(
        "SELECT COUNT(*) as count "
        "FROM likes "
        "WHERE postid = ? AND owner = ? ", (postid, flask.session['logname']))
    liked = cur.fetchall()
    if len(liked) != 1:
        flask.abort(409)
    if_liked = liked[0]['count']
    if operation == "like":
        if if_liked == 1:
            flask.abort(409)
        conn.execute("INSERT INTO likes (owner, postid) "
                     "VALUES (?, ?) ", (flask.session['logname'], postid))
    if operation == "unlike":
        if if_liked == 0:
            flask.abort(409)
        conn.execute("DELETE FROM likes "
                     "WHERE owner = ? AND postid = ? ",
                     (flask.session['logname'], postid))

    return flask.redirect(redirect_link)


@app.route("/posts/", methods=["POST"])
def post_handler():
    """Create or delete posts and redirect to URL.

    Returns:
        Response: rediect desitination
    """
    if "logname" not in flask.session:
        flask.abort(403)

    if 'target' not in flask.request.args:
        redirect_link = flask.url_for('show_profile',
                                      username=flask.session['logname'])
    else:
        redirect_link = flask.request.args['target']

    conn = get_db()
    postid = flask.request.form.get('postid')
    operation = flask.request.form['operation']
    if operation == 'create':
        if flask.request.files['file'].filename == "":
            flask.abort(400)
        filename = save_file_and_get_path(flask.request.files['file'])

        curr = conn.execute(
            "INSERT INTO posts(filename, owner) "
            "VALUES(?, ?)", (str(filename), flask.session['logname']))
    if operation == 'delete':
        curr = conn.execute("SELECT owner "
                            "FROM posts "
                            "WHERE postid = ?", (postid, ))
        owner_list = curr.fetchall()
        owner = owner_list[0]['owner']
        if owner != flask.session['logname']:
            flask.abort(403)
        curr = conn.execute(
            "SELECT filename, owner "
            "FROM posts "
            "WHERE postid = ? ", (postid, ))

        result = curr.fetchall()
        if result[0]['owner'] != flask.session['logname']:
            flask.abort(403)
        remove_file(result[0]['filename'])

        conn.execute("DELETE FROM posts "
                     "WHERE postid = ? ", (postid, ))

    return flask.redirect(redirect_link)


@app.route("/following/", methods=["POST"])
def following_handler():
    """Follow or unfollow the user.

    Returns:
        Response: redirecte destination
    """
    if 'logname' not in flask.session:
        flask.abort(403)

    if 'target' not in flask.request.args:
        redirect_link = flask.url_for('show_index')
    else:
        redirect_link = flask.request.args['target']

    operation = flask.request.form['operation']
    logname = flask.session['logname']
    username = flask.request.form['username']
    conn = get_db()
    if operation == "follow":
        conn.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES (?, ?)", (logname, username))
    elif operation == "unfollow":
        conn.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ? ", (logname, username))
    return flask.redirect(redirect_link)


def __account_login_request():
    logname = flask.request.form['username']
    password_local = flask.request.form['password']
    if not logname or not password_local:
        flask.abort(400)
    authenticate(logname, password_local)
    flask.session['logname'] = logname


def __account_create_request():
    fields = ["username", "password", "fullname", "email", "file"]
    for field in fields:
        if field == 'file':
            if flask.request.files['file'].filename == "":
                flask.abort(400)
        else:
            if flask.request.form[field] is None:
                flask.abort(400)

    # check whether this user exists
    conn = get_db()
    cur = conn.execute("SELECT username "
                       "FROM users "
                       "WHERE username = ?",
                       (flask.request.form['username'], ))
    user = cur.fetchall()
    if len(user) != 0:
        flask.abort(409)

    password_for_db = encrypt_password(flask.request.form['password'])

    # store file
    filename = save_file_and_get_path(flask.request.files['file'])

    # store all the files into database
    _ = conn.execute(
        "INSERT INTO users "
        "(username, password, fullname, filename, email) "
        "VALUES "
        "(?, ?, ?, ?, ?)", (flask.request.form['username'],
                            password_for_db, flask.request.form['fullname'],
                            str(filename), flask.request.form['email']))

    # create cookie for current user
    flask.session['logname'] = flask.request.form['username']


def __account_delete_request():
    if "logname" not in flask.session:
        flask.abort(403)
    conn = get_db()
    # get filename
    curr = conn.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username = ?", (flask.session['logname'], ))
    user = curr.fetchall()

    if len(user) == 0:
        # ! This shall never happen
        flask.abort(400)

    # delete file
    try:
        remove_file(user[0]['filename'])
    except FileNotFoundError:
        print(f"filename {user[0]['filename']} is not found")
        # ! This shall never happen
        flask.abort(404)

    # delete all the post file
    curr = conn.execute("SELECT filename "
                        "FROM posts "
                        "WHERE owner = ?", (flask.session['logname'], ))
    result = curr.fetchall()
    for item in result:
        remove_file(item['filename'])

    # delete item in database
    curr = conn.execute("DELETE FROM users "
                        "WHERE username = ?", (flask.session['logname'], ))
    flask.session.clear()


def __account_edit_request():
    # Check not login
    if 'logname' not in flask.session:
        flask.abort(403)

    # Check fullname and email are empty
    fields = ["fullname", "email"]
    for field in fields:
        if flask.request.form[field] is None:
            flask.abort(400)

    # Updatedb
    conn = get_db()

    if flask.request.files['file'].filename != "":
        result = conn.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?", (flask.session['logname'], ))

        # delete old photo
        file_name_old = result.fetchall()[0]['filename']
        remove_file(file_name_old)
        # Upload new photo
        new_file_path = save_file_and_get_path(flask.request.files['file'])

        result = conn.execute(
            "UPDATE users "
            "SET filename = ?, email = ?, fullname = ?"
            "WHERE username = ?",
            (str(new_file_path), flask.request.form['email'],
             flask.request.form['fullname'], flask.session['logname']))
    else:
        # Upload new name and email
        result = conn.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?",
            (flask.request.form['fullname'], flask.request.form['email'],
             flask.session['logname']))


def __account_update_password_request():
    # Check not login
    if 'logname' not in flask.session:
        flask.abort(403)

    # Check empty
    fields = ["password", "new_password1", "new_password2"]
    for field in fields:
        if field not in flask.request.form:
            flask.abort(400)

    # Check verification
    conn = get_db()
    cur = conn.execute("SELECT password "
                       "FROM users "
                       "WHERE username = ?", (flask.session['logname'], ))

    # check if old password matches
    pw_old_remote_encrypted = cur.fetchall()[0]['password']
    if not verify_password(flask.request.form['password'],
                           pw_old_remote_encrypted):
        flask.abort(403)

    # Check new_pw1 = new_pw2
    new_pw1 = flask.request.form['new_password1']
    new_pw2 = flask.request.form['new_password2']
    if new_pw1 != new_pw2:
        flask.abort(401)

    # Update db
    new_pw_encrypted = encrypt_password(new_pw1)
    cur = conn.execute(
        "UPDATE users "
        "SET password = ?  "
        "WHERE username = ?", (new_pw_encrypted, flask.session['logname']))


@app.route('/accounts/', methods=['POST'])
def account_handler():
    """Get request, update db, redirecte destination.

    Returns:
        Response: redirecte destination
    """
    if 'target' not in flask.request.args:
        redirect_link = flask.url_for('show_index')
    else:
        redirect_link = flask.request.args['target']

    operation = flask.request.form['operation']
    if operation == "login":
        __account_login_request()
    elif operation == "create":
        __account_create_request()
    elif operation == "delete":
        __account_delete_request()
    elif operation == "edit_account":
        __account_edit_request()
    elif operation == "update_password":
        __account_update_password_request()

    return flask.redirect(redirect_link)
