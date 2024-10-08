import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const navigate = useNavigate(); // Replaces useHistory

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Perform login logic here. This is just a mock check.
    if (email === 'test@example.com' && password === 'password') {
      setError('');
      // Redirect to dashboard or home
      navigate('/dashboard'); // Replaces history.push
    } else {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="login-container" >
      <h2>Login</h2>
      {error && <p>{error}</p>}
      <form onSubmit={handleLogin}>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            
          />
        </div>
        <div >
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
           
          />
        </div>
        <button type="submit" >Login</button>
      </form>
    </div>
  );
};


export default Login;
