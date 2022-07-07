import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Scroll extends React.Component {
  constructor(props) {
    super(props);
    this.state = { next: '', results: [], url: '' };
    this.handleScroll = this.handleScroll.bind(this);
    this.unloader = this.unloader.bind(this);
  }

  componentDidMount() {
    if (window.performance.getEntriesByType('navigation')[0].type !== 'back_forward') {
      const { url } = this.props;

      fetch(url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            next: data.next,
            results: data.results,
            url: data.url,
          });
        }).catch((error) => console.log(error));
    } else {
      this.setState(window.history.state);
    }
    window.addEventListener('beforeunload', this.unloader);
  }

  handleScroll() {
    const { next } = this.state;
    fetch(next, { method: 'GET', credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          next: data.next,
          results: prevState.results.concat(data.results),
          url: data.url,
        }));
        console.log(data.next);
      })
      .catch((error) => console.log(error));
  }

  unloader() {
    window.history.pushState(this.state, null);
  }

  render() {
    const { next, results } = this.state;
    return (
      <InfiniteScroll
        dataLength={results.length}
        next={this.handleScroll}
        hasMore={next !== ''}
        loader={<h4>Loading...</h4>}
      >
        {results.map((element) => (
          <Post key={element.postid} url={element.url} />
        ))}
      </InfiniteScroll>
    );
  }
}

Scroll.propTypes = {
  // next: PropTypes.string.isRequired,
  // results: PropTypes.ArrayOf(PropTypes.object).isRequired,
  url: PropTypes.string.isRequired,
};
export default Scroll;
