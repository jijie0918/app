import React from 'react';
import ReactDOM from 'react-dom';
import Scroll from './scroll';

// class PostWindow extends React.Component {
//   componentDidMount() {
//     // fetch all posts related to logname
//     const url = 'api/v1/posts/';
//     fetch(url, { credentials: 'same-origin' })
//     .then()
//   }
// }
// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM

  <Scroll url="/api/v1/posts/" />,
  document.getElementById('reactEntry'),
);
