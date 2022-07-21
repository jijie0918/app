"""REST API for comment."""
import json
import flask
from app import app
from app.models import get_db
from app.api.exceptions import BadRequestException
from app.api.exceptions import NotFoundException, ForbiddenException
from app.utils import authen_rest_api_and_get_logname


@app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def get_comment_api(commentid):
    """Delete comment in DB."""
    logname = authen_rest_api_and_get_logname()
    conn = get_db()
    curr = conn.execute("SELECT * "
                        "FROM comments "
                        "WHERE commentid=?", (commentid, ))
    item = curr.fetchone()
    if item is None:
        raise NotFoundException
    if item['owner'] != logname:
        raise ForbiddenException
    curr = conn.execute("DELETE "
                        "FROM comments "
                        "WHERE commentid=?", (commentid, ))
    return flask.jsonify({}), 204


@app.route('/api/v1/comments/', methods=['POST'])
def post_comment_api():
    """Add comment in DB and return comment."""
    logname = authen_rest_api_and_get_logname()
    if 'postid' not in flask.request.args:
        raise BadRequestException
    conn = get_db()
    text = json.loads(flask.request.data)['text']
    curr = conn.execute(
        "INSERT INTO comments(owner, postid, text) "
        "VALUES(?, ?, ?)", (logname, flask.request.args['postid'], text))
    context = {
        'commentid': curr.lastrowid,
        'lognameOwnsThis': True,
        'owner': logname,
        'ownerShowUrl': flask.url_for("show_profile", username=logname),
        'text': text,
        'url': flask.url_for('get_comment_api', commentid=curr.lastrowid)
    }
    return flask.jsonify(**context), 201
