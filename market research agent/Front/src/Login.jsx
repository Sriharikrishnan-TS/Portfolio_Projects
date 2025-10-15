import React, { useState } from 'react'; // Make sure to import useState
import './Login.css';

// 1. Accept the `onLogin` function as a prop
const Login = ({ onLogin }) => {
  // 2. Create state to hold the value of the username input
  const [username, setUsername] = useState('');

  // 3. This function will be called when the button is clicked
  const handleLoginClick = () => {
    // Call the onLogin function passed down from App.js, sending the username back up
    onLogin(username);
  };

  // Function to handle Enter key press
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleLoginClick();
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login Portal</h2>
        <p>Enter your credentials to continue.</p>
        <div className="input-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            placeholder="admin or customer"
            value={username} // Connect input value to state
            onChange={(e) => setUsername(e.target.value)} // Update state on change
            onKeyPress={handleKeyPress} // Add onKeyPress event
          />
        </div>
        <div className="input-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            placeholder="password"
            onKeyPress={handleKeyPress} // Add onKeyPress to password field as well
          />
        </div>
        {/* 4. Attach the click handler to the button's onClick event */}
        <button onClick={handleLoginClick} className="login-button">
          Login
        </button>
      </div>
    </div>
  );
};

export default Login;