import 'bootstrap/dist/css/bootstrap.min.css';
import './assets/mazer/css/mazer.min.css';
import './assets/mazers.js'
import React  from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
