import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChatInterface from './ChatInterface';
import AdminInterface from './AdminInterface';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<ChatInterface />} />
          <Route path="/admin" element={<AdminInterface />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;