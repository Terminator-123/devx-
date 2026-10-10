import React, { useState } from 'react';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import { Activity } from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home'); // home | analysis
  const [currentMatch, setCurrentMatch] = useState({
    matchId: null,
    filename: null,
    previewUrl: null,
    sport: 'badminton',
  });

  const handleNavigateToAnalysis = ({ matchId, filename, previewUrl, sport }) => {
    setCurrentMatch({ matchId, filename, previewUrl, sport });
    setCurrentPage('analysis');
  };

  const handleLoadSampleDemo = () => {
    setCurrentMatch({
      matchId: 'backup_demo',
      filename: 'sample_badminton_rally.mp4',
      previewUrl: null,
      sport: 'badminton',
    });
    setCurrentPage('analysis');
  };

  const handleBackToUpload = () => {
    setCurrentPage('home');
  };

  return (
    <div className="app-shell">
      {/* Top Navbar */}
      <nav className="navbar">
        <div className="nav-brand" onClick={() => setCurrentPage('home')}>
          <div className="brand-icon-wrapper">
            <Activity className="brand-icon" />
          </div>
          <div className="brand-text">
            <span className="brand-name">RallyLens</span>
            <span className="brand-tag">AI</span>
          </div>
        </div>

        <div className="nav-links">
          <button
            type="button"
            className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            Upload
          </button>
          {currentMatch.matchId && (
            <button
              type="button"
              className={`nav-btn ${currentPage === 'analysis' ? 'active' : ''}`}
              onClick={() => setCurrentPage('analysis')}
            >
              Dashboard (#{currentMatch.matchId})
            </button>
          )}
          <button
            type="button"
            className="nav-btn nav-btn-demo"
            onClick={handleLoadSampleDemo}
            title="Instant Badminton AI Demo Analysis"
          >
            ⚡ Live Demo
          </button>
        </div>
      </nav>

      {/* Main Content View */}
      <div className="app-content">
        {currentPage === 'home' ? (
          <Home
            onNavigateToAnalysis={handleNavigateToAnalysis}
            onLoadSampleDemo={handleLoadSampleDemo}
          />
        ) : (
          <Analysis
            matchId={currentMatch.matchId}
            initialVideoUrl={currentMatch.previewUrl}
            onBackToUpload={handleBackToUpload}
          />
        )}
      </div>

      <footer className="footer">
        <p>RallyLens AI • Elite Athletic Vision & Court Geometry Intelligence Platform • Multi-Frame Tracking & Tactical AI</p>
      </footer>
    </div>
  );
}
