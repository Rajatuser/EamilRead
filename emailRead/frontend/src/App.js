// src/App.js
import React, { useState } from 'react';
import EmailRead from './components/EmailRead';
import EmailDetails from './components/EmailDetails';
import './App.css';

const App = () => {
  const [selectedEmail, setSelectedEmail] = useState(null);

  return (
    <div>
      <EmailRead onSelectEmail={setSelectedEmail} />
      {/* <EmailDetails email={selectedEmail} /> */}
    </div>
  );
};

export default App;