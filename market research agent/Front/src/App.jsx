import React, { useState, useEffect } from "react";
import Login from "./Login";
import InterviewAgent from "./InterviewAgent";
import Dashboard from "./Dashboard";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState(null);

  // ✅ Check localStorage on refresh to persist login
  useEffect(() => {
    const storedRole = localStorage.getItem("userRole");
    if (storedRole) {
      setUserRole(storedRole);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = (username) => {
    const role = username.toLowerCase();
    if (role === "admin" || role === "customer") {
      setUserRole(role);
      setIsLoggedIn(true);
      localStorage.setItem("userRole", role); // ✅ Save to localStorage
    } else {
      alert('Invalid username. Please use "admin" or "customer".');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserRole(null);
    localStorage.removeItem("userRole"); // ✅ Clear on logout
  };

  const renderContent = () => {
    if (!isLoggedIn) {
      return <Login onLogin={handleLogin} />;
    }

    // ✅ Pass logout down to child components
    if (userRole === "admin") {
      return <Dashboard userRole={userRole} onLogout={handleLogout} />;
    } else {
      return <InterviewAgent userRole={userRole} onLogout={handleLogout} />;
    }
  };

  return <div className="App">{renderContent()}</div>;
}

export default App;
