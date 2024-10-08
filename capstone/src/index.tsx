import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Ensure this path is correct
import './index.css';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement // Type assertion
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Optional performance reporting
reportWebVitals();
