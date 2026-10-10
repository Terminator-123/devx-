import React, { useState } from 'react';
import VideoUpload from '../components/VideoUpload';
import ModelTrainingModal from '../components/ModelTrainingModal';
import { Target, Cpu, Clock, CheckCircle2, Database, Sparkles } from 'lucide-react';

export default function Home({ onNavigateToAnalysis, onLoadSampleDemo }) {
  const [showTrainingModal, setShowTrainingModal] = useState(false);

  return (
    <div className="page-home">
      <header className="hero-header">
        <div className="hero-top-action-bar">
          <div className="badge-pill">
            <span className="badge-dot" /> RallyLens AI • Single-Camera Tactical Intelligence
          </div>
          <button
            type="button"
            className="btn-open-training-modal"
            onClick={() => setShowTrainingModal(true)}
          >
            <Database className="btn-icon-xs text-indigo" />
            <span>Dataset Fine-Tuning (BFMD / SportsMOT / Shuttlecock)</span>
          </button>
        </div>

        <h1 className="hero-title">
          Badminton Multi-Frame Tracking & Tactical Analysis
        </h1>
        <p className="hero-description">
          Upload recorded match footage, record live with your mobile device or webcam, calibrate the 4 court corners, and review automated strength/weakness diagnostics.
        </p>
      </header>

      {showTrainingModal && (
        <ModelTrainingModal onClose={() => setShowTrainingModal(false)} />
      )}

      <main className="main-content">
        <VideoUpload
          onAnalysisStarted={(data) => {
            onNavigateToAnalysis(data);
          }}
          onUseSample={onLoadSampleDemo}
        />

        <div className="features-grid">
          <div className="feature-card">
            <Target className="feature-icon text-indigo" />
            <h3 className="feature-title">4-Corner Perspective Mapping</h3>
            <p className="feature-text">
              Collects top-left, top-right, bottom-right, and bottom-left points to project camera pixel coordinates into BWF court dimensions.
            </p>
          </div>
          <div className="feature-card">
            <Cpu className="feature-icon text-emerald" />
            <h3 className="feature-title">Persistent Multi-Frame Tracking</h3>
            <p className="feature-text">
              Tracks Player 1 and Player 2 across frames with foot-point estimation and ByteTrack-compatible temporal consistency.
            </p>
          </div>
          <div className="feature-card">
            <Clock className="feature-icon text-sky" />
            <h3 className="feature-title">Evidence-Linked Video Replay</h3>
            <p className="feature-text">
              Instantly jump to key rally timestamps by clicking on verified tactical timeline events.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
