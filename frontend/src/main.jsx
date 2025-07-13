import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx'; // Use .jsx if you chose JS template
import './index.css'; // This now imports Tailwind CSS

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);