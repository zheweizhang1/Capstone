import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [isRightPanelActive, setRightPanelActive] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate(); 

  const handleSignUpClick = () => {
    setRightPanelActive(true);
  };

  const handleSignInClick = () => {
    setRightPanelActive(false);
  };

  // Simulate sign-in function
  const handleSignIn = (e) => {
    e.preventDefault();
    console.log("Signing in with:", email, password);
    
    // Simulate successful sign-in and redirect to dashboard
    navigate("/dashboard"); // Redirect to dashboard after sign-in
  };

  // Simulate sign-up function (just for redirection for now)
  const handleSignUp = (e) => {
    e.preventDefault();
    console.log("Signing up...");
    
    // Simulate successful sign-up and redirect to dashboard
    navigate("/dashboard"); // Redirect to dashboard after sign-up
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
            <input type="text" placeholder="Username" required />
            <input type="password" placeholder="Password" required />
            <input type="text" placeholder="First Name" required />
            <input type="text" placeholder="Last Name" required />
            <input type="tel" placeholder="Contact Number" required />
            <input type="text" placeholder="Address 1" required />
            <input type="text" placeholder="Address 2" />
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
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
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
