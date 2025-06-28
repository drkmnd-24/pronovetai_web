import 'bootstrap/dist/css/bootstrap.min.css';
import '../public/mazer/css/mazer.min.css';
import '../public/mazer/css/mazers.js'
import React  from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
