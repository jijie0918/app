"""REST API for posts."""
import flask
from app import app
from app.utils import authen_rest_api_and_get_logname
from app.get_context import get_post_context
from app.api.exceptions import BadRequestException

INT_MAX = 2147483647


@app.route('/api/v1/posts/')
def get_newest_posts_api():
    """Return the 10 newest posts."""
    logname = authen_rest_api_and_get_logname()
    # set connection and authenticate the user
    conn = app.models.get_db()
    postid_lte = flask.request.args.get('postid_lte',
                                        default=INT_MAX,
                                        type=int)
    limit = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    if limit < 0 or page < 0:
        raise BadRequestException

    cur = conn.execute(
        "SELECT postid "
        "FROM posts "
        "WHERE (posts.owner = ? OR posts.owner IN "
        "(SELECT username2 "
        "FROM following "
        "WHERE username1 = ?)) "
        "AND postid <= ? "
        "ORDER BY postid DESC "
        "LIMIT ? "
        "OFFSET ? ", (logname, logname, postid_lte, limit, limit * page))
    posts = cur.fetchall()
    next_api = ""
    if len(posts) == limit and limit >= 1:
        postid_lte_next = postid_lte if postid_lte != INT_MAX else posts[0][
            'postid']
        next_api = flask.url_for(flask.request.endpoint,
                                 size=limit,
                                 page=page + 1,
                                 postid_lte=postid_lte_next)
    url = flask.request.full_path if flask.request.full_path.split(
        '/')[-1] != "?" else flask.request.path
    context = {"next": next_api, "results": [], "url": url}
    for post in posts:
        context['results'] += [{
            "postid":
            post["postid"],
            "url":
            flask.url_for("get_post_api", postid=post["postid"])
        }]
    return flask.jsonify(**context), 200


@app.route('/api/v1/posts/<int:postid>/')
def get_post_api(postid):
    """
    Return post on postid.

    """
    logname = authen_rest_api_and_get_logname()
    context = get_post_context(postid, for_api=True, logname=logname)
    return flask.jsonify(**context)
