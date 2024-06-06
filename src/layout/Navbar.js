import React from 'react';
import { Link } from 'react-router-dom';
import logo from './BLUR.png';
import '../App.css';

export default function Navbar() {
    return (
        <div>
            <nav className="navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: '#000000' }}>

                <div className="container-fluid">
                    <Link className="navbar-brand" to="/">
                        <img src={logo} alt="blur.com Logo" style={{ height: '60px' }} />
                    </Link>
                    <button
                        className="navbar-toggler"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#navbarSupportedContent"
                        aria-controls="navbarSupportedContent"
                        aria-expanded="false"
                        aria-label="Toggle navigation"
                    >
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                            {/* Add any other navbar items here if needed */}
                        </ul>
                        <div className="d-flex ms-auto">
                            <Link className='btn btn-outline-light mx-2' to="/eyesinvideo">👁️ in 🎥</Link>
                            <Link className='btn btn-outline-light mx-2' to="/facesinvideo">😀 in 🎥</Link>
                            <Link className='btn btn-outline-light mx-2' to="/specificfacesinvideo">🔍😀 in 🎥</Link>
                            <Link className='btn btn-outline-light mx-2' to="/redactspdf">📝✂️📄</Link>
                            <Link className='btn btn-outline-light mx-2' to="/eyesinpics">👁️ in 📸</Link>
                            <Link className='btn btn-outline-light mx-2' to="/facesinpics">😀 in 📸</Link>
                            <Link className='btn btn-outline-light mx-2' to="/specificfacesinpics">🔍😀 in 📸</Link>

                        </div>
                    </div>
                </div>
            </nav>
        </div>
    );
}
