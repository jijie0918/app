"""
login, logout, signup, delete, edit profile, change password view.

URLs include:
/accounts/login/
/accounts/logout/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
"""
import flask
from app import app
from app.models import get_db
from app.utils import redirect_to_login_if_session_is_not_valid


@app.route('/accounts/login/')
def login():
    """Render login template.

    Returns:
        Response: redirecte destination
        If login, return / page
    """
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Clear session and redirect to login page.

    Returns:
        Response: redirect destination
    """
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@app.route('/accounts/create/')
def signup():
    """Render template for signup.

    Returns:
        Response: redirection destination / render template
        If not login, return edit page
    """
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('edit_profile'))

    return flask.render_template("create_profile.html")


@app.route('/accounts/delete/')
def delete():
    """Render delete template.

    Returns:
        Response : rendered template
    """
    context = {"username": flask.session['logname']}
    return flask.render_template("delete.html", **context)


@app.route('/accounts/edit/')
def edit_profile():
    """Render edit profile template.

    Returns:
        Reponse: rendered template
        If not login, return login page
    """
    login_page = redirect_to_login_if_session_is_not_valid()
    if login_page is not None:
        return login_page

    # Get data
    connection = get_db()
    profile_info_result = connection.execute(
        "SELECT filename, email, fullname, username "
        "FROM users "
        "WHERE username = ? ", (flask.session['logname'], ))
    user = profile_info_result.fetchall()[0]
    username = flask.session['logname']
    context = {'user': user, 'username': username}
    return flask.render_template('edit.html', **context)


@app.route('/accounts/password/')
def password():
    """Render change password template.

    Returns:
        Response: rendered template
    """
    return flask.render_template('password.html')
