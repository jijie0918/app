"""REST API for likes."""
import flask
from app import app
from app.utils import authen_rest_api_and_get_logname
from app.api.exceptions import BadRequestException
from app.api.exceptions import NotFoundException, ForbiddenException


@app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def get_like_api(likeid):
    """Delete like in DB."""
    logname = authen_rest_api_and_get_logname()
    conn = app.models.get_db()
    curr = conn.execute("SELECT * "
                        "FROM likes "
                        "WHERE likeid = ?", (likeid, ))
    like_item = curr.fetchone()
    if like_item is None:
        raise NotFoundException
    if like_item['owner'] != logname:
        raise ForbiddenException
    curr = conn.execute("DELETE "
                        "FROM likes "
                        "WHERE likeid = ?", (likeid, ))
    context = {}
    return flask.jsonify(**context), 204


@app.route('/api/v1/likes/', methods=['POST'])
def post_like_api():
    """Add like in DB and return likeid, url."""
    if 'postid' not in flask.request.args:
        raise BadRequestException
    logname = authen_rest_api_and_get_logname()
    conn = app.models.get_db()
    curr = conn.execute("SELECT * "
                        "FROM likes l "
                        "INNER JOIN posts p "
                        "ON l.postid = p.postid "
                        "WHERE l.owner = ? AND p.postid = ? ",
                        (logname, flask.request.args['postid']))
    like_item = curr.fetchone()
    if like_item is not None:
        context = {
            'likeid': like_item['likeid'],
            'url': flask.url_for('get_like_api', likeid=like_item['likeid'])
        }
        # found like -> OK
        return flask.jsonify(**context), 200
    curr = conn.execute("INSERT INTO likes(owner, postid) "
                        "VALUES(?, ?)",
                        (logname, flask.request.args['postid']))
    context = {
        'likeid': curr.lastrowid,
        'url': flask.url_for('get_like_api', likeid=curr.lastrowid)
    }
    # created
    return flask.jsonify(**context), 201
