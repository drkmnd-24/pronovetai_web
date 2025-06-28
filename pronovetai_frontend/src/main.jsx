// --- 3rd-party CSS -------------------------------------------------
import 'bootstrap/dist/css/bootstrap.min.css';

// Mazer theme bundle
import './vendor/mazer/css/app.css';
import './vendor/mazer/css/app-dark.css';
import './vendor/mazer/css/auth.css';

// --- JS you actually write ----------------------------------------
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';

// (Optional) Bootstrap JS helpers – only if you rely on Collapse, Modal, etc.
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
