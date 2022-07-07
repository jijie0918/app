import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import { Comment, CommentForm } from './comment';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      comments: [],
      created: '',
      imgUrl: '',
      likes: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: '',
    };
    this.handleCommentSubmit = this.handleCommentSubmit.bind(this);
    this.handleCommentDelete = this.handleCommentDelete.bind(this);
    this.handleLike = this.handleLike.bind(this);
    this.handleDoubleLike = this.handleDoubleLike.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: data.comments,
          created: data.created,
          imgUrl: data.imgUrl,
          likes: data.likes,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
        });
      })
      .catch((error) => console.log(error));
  }

  handleCommentSubmit(body) {
    const { postid } = this.state;
    const url = `/api/v1/comments/?postid=${postid}`;
    fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then((response) => {
      if (response.status !== 201) {
        throw new Error(response.statusText);
      }
      console.log(response);
      return response.json();
    }).then((data) => {
      // const { comments } = this.state;
      this.setState((prevState) => ({
        comments: prevState.comments.concat(data),
      }));
    })
      .catch((error) => console.log(error));
  }

  handleCommentDelete(url, commentid) {
    fetch(url, {
      method: 'DELETE', credentials: 'same-origin',
    }).then((response) => {
      if (response.status !== 204) {
        throw new Error(response.statusText);
      } else {
        this.setState((prevState) => ({
          comments: prevState.comments.filter((comment) => comment.commentid !== commentid),
        }));
      }
    });
  }

  handleLike() {
    const {
      likes, postid,
    } = this.state;
    if (likes.lognameLikesThis) {
      fetch(
        likes.url,
        { method: 'DELETE', credentials: 'same-origin' },
      ).then(
        (response) => {
          if (response.status !== 204) {
            throw new Error(response.statusText);
          }
          const newLikes = {
            lognameLikesThis: false,
            numLikes: likes.numLikes - 1,
            url: null,
          };
          this.setState({ likes: newLikes });
        },
      ).catch((error) => {
        console.error('Error:', error);
      });
    } else {
      fetch(
        `/api/v1/likes/?postid=${postid}`,
        {
          method: 'POST', credentials: 'same-origin',
        },
      ).then((response) => {
        if (response.status !== 201) {
          throw new Error(response.statusText);
        }
        return response.json();
      }).then((data) => {
        const newLikes = {
          lognameLikesThis: true,
          numLikes: likes.numLikes + 1,
          url: data.url,
        };
        this.setState({
          likes: newLikes,
        });
      }).catch((error) => {
        console.error('Error:', error);
      });
    }
  }

  handleDoubleLike() {
    const {
      likes, postid,
    } = this.state;
    if (likes.lognameLikesThis === false) {
      fetch(
        `/api/v1/likes/?postid=${postid}`,
        {
          method: 'POST', credentials: 'same-origin',
        },
      ).then((response) => {
        if (response.status !== 201) {
          throw new Error(response.statusText);
        }
        return response.json();
      }).then((data) => {
        const newLikes = {
          lognameLikesThis: true,
          numLikes: likes.numLikes + 1,
          url: data.url,
        };
        this.setState({
          likes: newLikes,
        });
      }).catch((error) => {
        console.error('Error:', error);
      });
    }
  }

  renderBanner() {
    const {
      ownerShowUrl, created, ownerImgUrl, owner, postShowUrl,
    } = this.state;
    return (
      <div className="d-flex justify-content-between p-2 px-3">
        <div className="d-flex flex-row align-items-center">
          <div className="p-1">
            <a href={ownerShowUrl}>
              <img src={ownerImgUrl} alt="owner_img_url" className="profile-image rounded-circle" width="40px" height="40px" />
            </a>
          </div>
          <div className="p-1">
            <a href={ownerShowUrl}>
              <span className="font-weight-bold">{owner}</span>
            </a>
          </div>
        </div>
        <div className="d-flex flex-row mt-1 align-items-center">
          <small>
            <a style={{ color: '#AAA' }} href={postShowUrl}>
              {' '}
              {moment(created).fromNow()}
              {' '}
            </a>
          </small>
        </div>
      </div>
    );
  }

  renderLikeReact() {
    const { likes } = this.state;
    let likeContent;
    if (likes.lognameLikesThis) {
      likeContent = 'unlike';
    } else {
      likeContent = 'like';
    }
    return (
      <button type="button" className="like-unlike-button btn btn-light" onClick={this.handleLike}>
        {likeContent}
      </button>
    );
  }

  renderCommentsAndLikes() {
    const { likes, comments } = this.state;
    let likeNum;
    if (likes.numLikes === 1) {
      likeNum = (
        <p>
          {likes.numLikes}
          {' '}
          like
        </p>
      );
    } else {
      likeNum = (
        <p>
          {likes.numLikes}
          {' '}
          likes
        </p>
      );
    }
    // render comments
    const commentsComponent = comments
      .map((comment) => (
        <Comment
          key={comment.commentid}
          owner={comment.owner}
          ownerShowUrl={comment.ownerShowUrl}
          text={comment.text}
          lognameOwnsThis={comment.lognameOwnsThis}
          commentDeleteHandler={this.handleCommentDelete}
          commentid={comment.commentid}
          url={comment.url}
        />
      ));
    return (
      <div className="p-4">
        <div>
          {likeNum}
        </div>
        <div>
          {commentsComponent}
        </div>
        <div className="col-sm-2 py-2">
          {this.renderLikeReact()}
        </div>
        <CommentForm formHandler={this.handleCommentSubmit} />
      </div>
    );
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    // Render number of post image and post owner
    const { imgUrl } = this.state;
    return (
      <div className="card my-2">
        {this.renderBanner()}
        <div className="row">
          <img className="img-fluid" src={imgUrl} alt="img_url" onDoubleClick={this.handleDoubleLike} />
        </div>
        {this.renderCommentsAndLikes()}
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
