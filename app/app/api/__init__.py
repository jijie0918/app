"""REST API"""

from app.api.posts import get_newest_posts_api, get_post_api
from app.api.comments import get_comment_api, post_comment_api
from app.api.likes import get_like_api, post_like_api
from app.api.index import get_api