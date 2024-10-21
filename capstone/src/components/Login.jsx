import { logInAPI, signUpAPI } from '../api';

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [isRightPanelActive, setRightPanelActive] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate(); 

  const handleSignUpClick = () => {
    setRightPanelActive(true);
  };

  const handleSignInClick = () => {
    setRightPanelActive(false);
  };

  // Simulate sign-in function
  const handleSignIn = async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);  // Extract form data
    const values = {
      username: formData.get('loginUsername'),
      password: formData.get('loginPassword')
    };
    console.log("Logging in with:", values.username, values.password);
    
    try {
      // const response = await axios.post("localhost:5000/api/user", values);
      const response = await logInAPI(values); // Uses the logInAPI function from api.js
      console.log('User logged in:', response);
      navigate('/dashboard', { state: { firstname: response.firstname, username: response.username } });
    } catch (error) {
      console.error("Error logging in at Logsin.jsx:", error);
    }
  };

  // Simulate sign-up function (just for redirection for now)
  const handleSignUp = async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);  // Extract form data
    const values = {
      username: formData.get('username'),
      password: formData.get('password'),
      firstname: formData.get('firstname'),
      lastname: formData.get('lastname'),
      email: formData.get('email'),
      phonenumber: formData.get('phonenumber'),
      address1: formData.get('address1'),
      address2: formData.get('address2')
    };
    console.log("Signing up...");
    
    try {
      // const response = await axios.post("localhost:5000/api/user", values);
      const response = await signUpAPI(values); // Use the createUser function from api.js
      console.log('User signed up:', response);
      navigate('/dashboard', { state: { firstname: response.firstname, username: response.username } });
    } catch (error) {
      console.error("Error signning up at Logsin.jsx:", error);
    }

    // navigate("/dashboard"); // Redirect to dashboard after sign-up
  };

  return (
    <div className="body-container">
      <div
        className={`container ${
          isRightPanelActive ? "right-panel-active" : ""
        }`}
      >
        {/* Sign Up Form */}
        <div className="form-container sign-up-container">
          <form onSubmit={handleSignUp}>
            <h1>Create Account</h1>
            <input type="text" name="username" placeholder="Username" required />
            <input type="password" name="password" placeholder="Password" required />
            <input type="text" name="firstname" placeholder="First Name" required />
            <input type="text" name="lastname" placeholder="Last Name" required />
            <input type="text" name="email" placeholder="Email" required />
            <input type="tel" name="phonenumber" placeholder="Contact Number" required />
            <input type="text" name="address1" placeholder="Address 1" required />
            <input type="text" name="address2" placeholder="Address 2" />
            <button type="submit" className="btn-grad">
              Sign Up
            </button>
          </form>
        </div>

        {/* Sign In Form */}
        <div className="form-container sign-in-container">
          <form onSubmit={handleSignIn}>
            <h1>Sign In</h1>
            <input
              type="username"
              name="loginUsername"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              name="loginPassword"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <a href="#">Forgot your password?</a>
            <button type="submit" className="btn-grad">
              Sign In
            </button>
          </form>
        </div>

        {/* Overlay */}
        <div className="overlay-container">
          <div className="overlay">
            <div className="overlay-panel overlay-left">
              <h1>Welcome Back!</h1>
              <p>Start from where you left</p>
              <div className="btn-grad" onClick={handleSignInClick}>
                Sign In
              </div>
            </div>
            <div className="overlay-panel overlay-right">
              <h1>Hello!</h1>
              <p>Join Us</p>
              <div className="btn-grad" onClick={handleSignUpClick}>
                Sign Up
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
