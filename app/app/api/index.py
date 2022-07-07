"""REST API to return a list of services available."""
import flask
from app import app


@app.route("/api/v1/")
def get_api():
    """Return a list of services available."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)
