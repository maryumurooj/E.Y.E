import React from 'react';
import GestureControl from './components/GestureControl';
import "./App.css"
import logo from "./assets/logo.png"

const App = () => {


  return (
    <div className="App">
     
        <img src={logo} alt="" />
      
      <header className="App-header">
        <h1> E.Y.E. </h1>
        <h2>Sign Language to Speech</h2>
        <GestureControl />
      </header>
    </div>
  );
};

export default App;
