// src/components/EmailDetails.js
import React from 'react';

const EmailDetails = ({ email }) => {
  if (!email) {
    return <div className="container">Select an email to view details.</div>;
  }

  return (
    <div className="email-details container">
      <h2>{email.subject}</h2>
      <p><strong>From:</strong> {email.sender}</p>
      <p><strong>Date:</strong> {new Date(email.date).toLocaleString()}</p>
      <div>
        <h3>Message:</h3>
        <p>{email.body}</p>
      </div>
    </div>
  );
};

export default EmailDetails;