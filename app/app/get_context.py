"""Get post context."""
import flask
import arrow
from app import app
from app.models import get_db
from app.api.exceptions import NotFoundException


def get_post_context(postid, logname, for_api=False):
    """Get post context."""
    # Connect to database
    conn = get_db()
    # Get post
    post = conn.execute(
        "SELECT filename AS post_filename, owner, created, postid "
        "FROM posts "
        "WHERE postid = ?", (postid, )).fetchone()
    if post is None and for_api:
        raise NotFoundException

    # Get owner_img_url
    profile_filename = conn.execute(
        "SELECT filename as profile_filename "
        "FROM users "
        "WHERE username = ?", (post['owner'], )).fetchone()['profile_filename']

    # Get likes
    like_result = conn.execute(
        "SELECT owner, likeid "
        "FROM likes "
        "WHERE postid = ?", (postid, )).fetchall()

    logname_like_post = False
    likeid = None

    for item in like_result:
        if item['owner'] == logname:
            logname_like_post = True
            likeid = item['likeid']
            break

    num_likes = len(like_result)

    # Get comments
    comments = conn.execute(
        "SELECT owner, text, commentid "
        "FROM comments "
        "WHERE postid = ?", (postid, )).fetchall()

    # Add database info to context
    if for_api:
        likes = {
            'lognameLikesThis':
            logname_like_post,
            'numLikes':
            num_likes,
            'url':
            flask.url_for('get_like_api', likeid=likeid)
            if logname_like_post else None
        }
        for comment in comments:
            comment.update({
                'lognameOwnsThis':
                logname == comment['owner'],
                'ownerShowUrl':
                flask.url_for('show_profile', username=comment['owner']),
                'url':
                flask.url_for('get_comment_api',
                              commentid=comment['commentid'])
            })
        context = {
            'comments': comments,
            'created': post['created'],
            'imgUrl': f"/uploads/{post['post_filename']}",
            'likes': likes,
            'owner': post['owner'],
            'ownerImgUrl': f"/uploads/{profile_filename}",
            'ownerShowUrl': flask.url_for('show_profile',
                                          username=post['owner']),
            'postShowUrl': flask.url_for('show_post', postid=post['postid']),
            'postid': post['postid'],
            'url': flask.url_for('get_post_api', postid=post['postid'])
        }
    else:
        post['created'] = arrow.get(post['created']).humanize()
        context = {
            "post": post,
            "comments": comments,
            "likes": num_likes,
            "profile_filename": profile_filename,
            "logname_like_posts": logname_like_post
        }
    return context
