import './App.css';
// import React, { Component } from 'react';




const PAGES = {
  welcome: 'Welcome',
  experiment: 'Experiment',
  about: 'About',
  survey: 'Survey',
  thanks: 'Thanks'
}


// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }



import React, { useState, useEffect } from 'react';
import './App.css';
import { API } from 'aws-amplify';
import { withAuthenticator, AmplifySignOut } from '@aws-amplify/ui-react';
import { GetRecipeDetail } from 'lambda/GetRecipeDetail';
// import { createNote as createNoteMutation, delete?Note as deleteNoteMutation } from './graphql/mutations';


const initialFormState = { name: '', description: '' }

function App() {
  const [notes, setNotes] = useState([]);
  const [formData, setFormData] = useState(initialFormState);

  useEffect(() => {
    fetchNotes();
  }, []);

  async function fetchNotes() {
    const apiData = await API.graphql({ query: GetRecipeDetail });
    setNotes(apiData.data.listNotes.items);
  }

  // async function createNote() {
  //   if (!formData.name || !formData.description) return;
  //   await API.graphql({ query: createNoteMutation, variables: { input: formData } });
  //   setNotes([ ...notes, formData ]);
  //   setFormData(initialFormState);
  // }

  // async function deleteNote({ id }) {
  //   const newNotesArray = notes.filter(note => note.id !== id);
  //   setNotes(newNotesArray);
  //   await API.graphql({ query: deleteNoteMutation, variables: { input: { id } }});
  // }

  return (
    <div className="App">
      <h1>My Notes App</h1>
      <input
        onChange={e => setFormData({ ...formData, 'name': e.target.value})}
        placeholder="Note name"
        value={formData.name}
      />
      <input
        onChange={e => setFormData({ ...formData, 'description': e.target.value})}
        placeholder="Note description"
        value={formData.description}
      />
      <button onClick={createNote}>Create Note</button>
      <div style={{marginBottom: 30}}>
        {
          notes.map(note => (
            <div key={note.id || note.name}>
              <h2>{note.name}</h2>
              <p>{note.description}</p>
              <button onClick={() => deleteNote(note)}>Delete note</button>
            </div>
          ))
        }
      </div>
      <AmplifySignOut />
    </div>
  );
}

export default withAuthenticator(App);



// class Page extends Component {

//   constructor(props) {
//     super(props);
//     this.state = {
//       page: PAGES.welcome,
//       demographic: null,
//       dataset: [],
//       // sessionID: SESSION_ID,
//     }
//   }

//   handleSurvey = response => {
//     this.setState({ demographic: response });
//     this.setPage(PAGES.experiment);
//   }

//   handleDataset = dataset => {
//     this.setState({ dataset: dataset });
//   }

//   resetData = () => {
//     this.setState({dataset: []});
//   }

//   setPage = newPage => {
//     this.setState({ page: newPage });
//     document.getElementById(newPage).classList.add('curPage');
//   }

//   renderContent() {
//     switch (this.state.page) {
//       case PAGES.welcome:
//         return <Welcome setPage={this.setPage} />
//       case PAGES.experiment:
//         return (
//           <Survey
//             demographic={this.state.demographic}
//             handleSurvey={this.handleSurvey}
//           />
//         );
//       case PAGES.survey:
//         return (
//           <Survey
//             demographic={this.state.demographic}
//             handleSurvey={this.handleSurvey}
//           />
//         );
//       case PAGES.about:
//         return (
//         <Survey
//           demographic={this.state.demographic}
//           handleSurvey={this.handleSurvey}
//         /> 
//         );
//       case PAGES.thanks:
//         return (
//         <Survey
//           demographic={this.state.demographic}
//           handleSurvey={this.handleSurvey}
//         />
//         );
//       default:
//         return (
//           <div>
//             <h2>Lost</h2>
//             <p>Please select a page from the top bar to continue.</p>
//           </div>
//         )
//     }
//   }

//   render() {
//     return (
//       <div>
//         <div className="top-bar">
//           <div className="top-bar-left">
//             <ul className="menu">
//               <li className="menu-text">CS 573 Data Vis Project 3</li>
//               <li><button id="Welcome" className="" class="button curPage">Welcome</button></li>
//               <li><button id="Survey" className="button">Background Survey</button></li>
//               <li><button id="Experiment" className="button">Experiment</button></li>
//               <li><button id="Thanks" className="button">Thanks!</button></li>
//             </ul>
//           </div>
//         </div>
//         <div className="page-container">
//           {this.renderContent()}
//         </div>
//       </div>
//     )
//   }
// }



// function Welcome(props) {
//   document.title = "CS 573 - Welcome"
//   return (
//     <div>
//       <h2>Welcome!</h2>
//       <p>
//         Welcome to our Data Vis Project! Thank you for taking a few minutes of
//         your day to help us out. This website is a replication of 
//         <a href="https://www.jstor.org/stable/2288400?seq=1" rel="noopener noreferrer" target="_blank"> a paper on Graphical 
//         Perception by Cleaveland and McGill.</a> This is part of an assignment
//         for CS 573 Data Visualization and was created by Imogen Cleaver-Stigum, Andrew Nolan, Matt St.
//         Louis, and Jyalu Wu. For the best experience, please use a laptop or a computer instead of a mobile device.
//       </p>
//       {/* <img src={team_members} alt="Picture of the team members"></img> */}
//       <br></br><br></br>
//       <button type="button" className="button" onClick={() => props.setPage(PAGES.survey)}>
//         Get Started
//       </button>
//     </div>
//   )
// }



// class Survey extends Component {
//   constructor(props) {
//     document.title = "Background Survey"
//     super(props);
//     this.state = {
//       familiarity: 'No Formal Education',
//       education: 'No Formal Stats Training',
//       stats: 'Not familiar',
//       field: ''
//     }
//   }

//   handleChangeFamiliarity = e => {
//     this.setState({
//       familiarity: e.target.value,
//     })
//   }

//   handleChangeEducation = e => {
//     this.setState({
//       education: e.target.value,
//     })
//   }

//   handleChangeStats = e => {
//     this.setState({
//       stats: e.target.value,
//     })
//   }

//   handleChangeField = e => {
//     this.setState({
//       field: e.target.value,
//     })
//   }

//   fieldIsValid = () => {
//     return this.state.field !== "" && this.state.field !== undefined;
//   }

//   render() {
//     return (
//       <div>
//         <h2>Background Survey</h2>
//         <form>
//           <label>
//             What is the highest education level you are currently pursuing or have achieved?
//           <select value={this.state.education} onChange={this.handleChangeEducation}>
//               <option value="No Formal Education">
//                 No Formal Education
//             </option>
//               <option value="High School">
//                 High School
//             </option>
//               <option value="Bacherlors Degree (BA)">
//                 Bachelors Degree (BA)
//             </option>
//               <option value="Bachelors Degree (BS)">
//                 Bachelors Degree (BS)
//             </option>
//               <option value="Vocational Training">
//                 Vocational Training
//             </option>
//               <option value="Masters Degree">
//                 Masters Degree
//             </option>
//               <option value="PhD/Doctorate">
//                 PhD/Doctorate
//             </option>
//             </select>
//           </label>
//           <label>
//             How familiar are you with statistics?
//           <select value={this.state.stats} onChange={this.handleChangeStats}>
//               <option value="No Formal Stats Training">
//                 No Formal Stats Training
//             </option>
//               <option value="Some Basic Statistics Training">
//                 Some Basic Statistics Training
//             </option>
//               <option value="A lot of statistics experience">
//                 A lot of statistics experience
//             </option>
//               <option value="I use statistics everyday">
//                 I use statistics everyday
//             </option>
//             </select>
//           </label>
//           <label>
//             How familiar would you say you are with data visualizations?
//           <select value={this.state.familiarity} onChange={this.handleChangeFamiliarity}>
//               <option value="Not familiar">
//                 Not familiar
//             </option>
//               <option value="Passing Knowledge">
//                 Passing Knowledge
//             </option>
//               <option value="Knowledgable">
//                 Knowledgable
//             </option>
//               <option value="Expert">
//                 Expert
//             </option>
//             </select>
//           </label>
//           <label>
//             What is your area of study or field you work in?
//           <input type="text" onChange={this.handleChangeField}></input>
//           </label>
//           <button type="submit" className="button" onClick={() => this.props.handleSurvey(this.state)} disabled={!this.fieldIsValid()}>Submit</button>
//         </form>
//       </div>
//     )
//   }
// }



// class App extends Component {

//   state = {
//     inputText: "",
//     test: "test"
//   }

//   changeText = e => {
//     this.setState({
//       inputText: e.target.value
//     });
//   }

//   uploadToFirebase = e => {
//     // let dataRef = fire.database().ref('data').orderByKey();
//     // fire.database().ref('data').push(this.state);
//     // this.setState({
//     // });
//   }

//   render() {
//     return (
//       <div>
//         {/* <div className="App-header"> */}
//         {/* <input type="text" id="inputText" onChange={this.changeText}></input> */}
//         {/* <br/> */}
//         {/* <button onClick={this.submit}>Submit Data</button> */}
//         {/* </div> */}
//         <Page />
//       </div>
//     );
//   }
// }

// export default App;
