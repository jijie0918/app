import React from 'react';
import PropTypes from 'prop-types';

function Comment(props) {
  const {
    owner, ownerShowUrl, text, lognameOwnsThis, commentDeleteHandler, url, commentid,
  } = props;
  let deleteButton;
  if (lognameOwnsThis) {
    deleteButton = (
      <button type="button" onClick={() => commentDeleteHandler(url, commentid)} className="delete-comment-button btn btn-light mw-3">
        Delete comment
      </button>
    );
  } else {
    deleteButton = null;
  }
  return (
    <div className="d-flex flex-row align-items-baseline">
      <div className="d-flex flex-row text-justify">
        <p className="me-2">
          <a href={ownerShowUrl}>{ owner }</a>
        </p>
        <p>
          { text }
        </p>
      </div>
      <div className="mx-2">
        {deleteButton}
      </div>
    </div>
  );
}

class CommentForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { content: '' };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  handleSubmit(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const { formHandler } = this.props;
      const body = { text: event.target.value };
      this.setState({ content: '' });
      formHandler(body);
    }
  }

  handleChange(event) {
    this.setState({ content: event.target.value });
  }

  render() {
    const { content } = this.state;
    return (
      <form className="comment-form">
        <div className="row py-1">
          <div className="form-group col-sm-9">
            <input type="text" value={content} className="form-control" name="text" onKeyPress={this.handleSubmit} onChange={this.handleChange} />
          </div>
        </div>
      </form>
    );
  }
}

Comment.propTypes = {
  owner: PropTypes.string.isRequired,
  ownerShowUrl: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  lognameOwnsThis: PropTypes.bool.isRequired,
  commentDeleteHandler: PropTypes.func.isRequired,
  url: PropTypes.string.isRequired,
  commentid: PropTypes.number.isRequired,
};

CommentForm.propTypes = {
  formHandler: PropTypes.func.isRequired,
};

export { Comment, CommentForm };
