import React, { Component } from 'react';
import Contacts from './components/contacts';

class App extends Component {
    state = {
        contacts: []
    }
  render() {

      fetch('https://lkt9ygcr5g.execute-api.us-east-2.amazonaws.com/beta/recipes')
          .then(res => res.json())
          .then((data) => {
              this.setState({ contacts: data.items})
          })
          .catch(console.log)
        return (
            <Contacts contacts={this.state.contacts} />
    )
  }
}


export default App;

//
// 'http://jsonplaceholder.typicode.com/users'

// https://lkt9ygcr5g.execute-api.us-east-2.amazonaws.com/beta/recipes