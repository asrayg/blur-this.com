// src/components/Home.js
import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../App.css';

export default function Home() {
  return (
    <div className="shiny-background">
      <div>
        <h1>Welcome to Blur.com</h1>
        <p>
          Our application offers state-of-the-art privacy solutions to protect your sensitive information. 
          Whether you need to blur faces or eyes in images and videos, redact confidential information in PDFs, 
          or ensure specific individuals are obscured, our tools are designed to meet your privacy needs. 
          Leveraging advanced models and robust algorithms, we provide reliable and efficient processing to safeguard your data.
        </p>
      </div>
    </div>
  );
}
