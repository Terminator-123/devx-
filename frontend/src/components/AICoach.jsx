import React, { useState } from 'react';
import { Award, Zap, AlertTriangle, ShieldCheck, Dumbbell, Compass, HelpCircle } from 'lucide-react';

export default function AICoach({ aiCoach, durationSeconds = 0 }) {
  const [selectedTab, setSelectedTab] = useState('insights'); // insights | drills

  if (!aiCoach) {
    return (
      <div className="coach-panel-empty">
        <Compass className="empty-icon animate-pulse" />
        <p>AI Tactical Coach report will be generated upon video tracking completion.</p>
      </div>
    );
  }

  const {
    tactical_summary,
    strengths = [],
    weaknesses = [],
    actionable_drills = [],
    fatigue_or_pace_rating = 'Moderate',
    player_target = 'Player 1'
  } = aiCoach;

  return (
    <div className="ai-coach-card">
      <div className="coach-card-header">
        <div className="header-left">
          <div className="coach-badge-icon">
            <Award className="icon-main text-emerald" />
          </div>
          <div>
            <h3 className="coach-title">AI Tactical Coach & Skill Diagnostic</h3>
            <span className="coach-subtitle">Targeting: <strong>{player_target}</strong> • Pace Rating: <span className="pace-pill">{fatigue_or_pace_rating}</span></span>
          </div>
        </div>

        <div className="coach-tab-pills">
          <button
            type="button"
            className={`tab-pill-btn ${selectedTab === 'insights' ? 'active' : ''}`}
            onClick={() => setSelectedTab('insights')}
          >
            Strengths & Weaknesses
          </button>
          <button
            type="button"
            className={`tab-pill-btn ${selectedTab === 'drills' ? 'active' : ''}`}
            onClick={() => setSelectedTab('drills')}
          >
            Targeted Drills ({actionable_drills.length})
          </button>
        </div>
      </div>

      {/* Tactical Summary */}
      <div className="coach-summary-box">
        <p className="summary-text">{tactical_summary}</p>
      </div>

      {selectedTab === 'insights' ? (
        <div className="coach-insights-grid">
          {/* Strengths */}
          <div className="strengths-col">
            <div className="col-header strengths-hdr">
              <ShieldCheck className="col-icon" />
              <h4>Identified Strengths ({strengths.length})</h4>
            </div>
            <ul className="coach-item-list">
              {strengths.map((s, idx) => (
                <li key={idx} className="coach-item strength-item">
                  <span className="bullet-dot bg-emerald"></span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Weaknesses */}
          <div className="weaknesses-col">
            <div className="col-header weaknesses-hdr">
              <AlertTriangle className="col-icon" />
              <h4>Areas for Tactical Improvement ({weaknesses.length})</h4>
            </div>
            <ul className="coach-item-list">
              {weaknesses.map((w, idx) => (
                <li key={idx} className="coach-item weakness-item">
                  <span className="bullet-dot bg-amber"></span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="drills-section">
          <div className="drills-header">
            <Dumbbell className="drill-icon" />
            <h4>Prescribed Corrective Training Drills</h4>
          </div>
          <div className="drills-cards-grid">
            {actionable_drills.map((drill, idx) => (
              <div key={idx} className="drill-card">
                <span className="drill-num">0{idx + 1}</span>
                <p className="drill-desc">{drill}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
