/**
 * Main entry point for the React application.
 * 
 * Educational Note: This is where the React app is mounted to the DOM.
 * We use React 18's createRoot API for concurrent features.
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
