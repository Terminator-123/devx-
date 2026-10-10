import React from 'react';
import { Play, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

export default function EvidenceTimeline({ events = [], onSeekToEvent, activeEventId }) {
  const formatSecs = (sec) => {
    const s = Number(sec) || 0;
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    const tenths = Math.floor((s % 1) * 10);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${tenths}`;
  };

  return (
    <div className="evidence-panel">
      <div className="evidence-header">
        <div className="evidence-title-group">
          <Clock className="evidence-icon text-primary" />
          <h4 className="evidence-title">Tactical Movement Observations</h4>
        </div>
        <span className="evidence-count">{events.length} Evidence Events</span>
      </div>

      <div className="evidence-list">
        {events.length === 0 ? (
          <div className="empty-state-text">No movement events detected for this recording.</div>
        ) : (
          events.map((evt) => {
            const isActive = activeEventId === evt.id;
            const hasConf = evt.confidence !== undefined && evt.confidence !== null;

            return (
              <div
                key={evt.id}
                className={`evidence-card-item ${isActive ? 'active-row' : ''}`}
                onClick={() => onSeekToEvent(evt.start_seconds, evt.id)}
              >
                <div className="evidence-row">
                  <div className="evidence-left">
                    <span className="event-type-tag">{evt.type || 'movement'}</span>
                    <span className="event-title-text">{evt.title}</span>
                    <span className="event-time-span">
                      {formatSecs(evt.start_seconds)} → {formatSecs(evt.end_seconds)}
                    </span>
                  </div>

                  <div className="evidence-right">
                    {hasConf ? (
                      <span className="event-conf-pill">{Math.round(evt.confidence * 100)}% Conf</span>
                    ) : (
                      <span className="event-conf-warn">{evt.quality || 'Observed'}</span>
                    )}
                    <button
                      type="button"
                      className="btn-seek-action"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSeekToEvent(evt.start_seconds, evt.id);
                      }}
                      title={`Seek video to ${formatSecs(evt.start_seconds)}`}
                    >
                      <Play className="seek-play-icon" /> Seek & Play
                    </button>
                  </div>
                </div>

                {/* Rally Evidence Loop details: Measured pattern & Coaching suggestion */}
                {(evt.measured_pattern || evt.coaching_suggestion) && (
                  <div className="evidence-coaching-box">
                    {evt.measured_pattern && (
                      <div className="measured-pattern-line">
                        <span className="meta-lbl">Measured Observation:</span> {evt.measured_pattern}
                      </div>
                    )}
                    {evt.coaching_suggestion && (
                      <div className="coaching-suggestion-line">
                        <span className="coaching-lbl">Coaching Suggestion:</span> {evt.coaching_suggestion}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
