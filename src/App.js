// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './layout/Navbar';
import Home from './pages/Home';
import EyesInVideo from './pages/Eyesinvideo';
import FacesInVideo from './pages/Facesinvideo';
import SpecificFacesInVideo from './pages/Specificfacesinvideo';
import RedactPdf from './pages/Redactspdf';
import EyesInPics from './pages/Eyesinpics';
import FacesInPics from './pages/Facesinpics';
import SpecificFacesInPics from './pages/Specificfacesinpics';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route exact path="/" element={<Home />} />
        <Route path="/eyesinvideo" element={<EyesInVideo />} />
        <Route path="/facesinvideo" element={<FacesInVideo />} />
        <Route path="/specificfacesinvideo" element={<SpecificFacesInVideo />} />
        <Route path="/redactspdf" element={<RedactPdf />} />
        <Route path="/eyesinpics" element={<EyesInPics />} />
        <Route path="/facesinpics" element={<FacesInPics />} />
        <Route path="/specificfacesinpics" element={<SpecificFacesInPics />} />
      </Routes>
    </Router>
  );
};

export default App;
