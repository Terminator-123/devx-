import React, { useState, useEffect, useRef } from 'react';
import MetricCard from '../components/MetricCard';
import CourtHeatmap from '../components/CourtHeatmap';
import EvidenceTimeline from '../components/EvidenceTimeline';
import { getStatus, getResults, getMediaVideoUrl, getMediaAnnotatedUrl } from '../api';
import { ArrowLeft, Loader2, AlertCircle, AlertTriangle, CheckCircle2, Video } from 'lucide-react';

export default function Analysis({ matchId, initialVideoUrl, onBackToUpload }) {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('processing');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeEventId, setActiveEventId] = useState(null);
  const [videoMode, setVideoMode] = useState('annotated'); // annotated | original
  const [currentTime, setCurrentTime] = useState(0);

  const videoRef = useRef(null);

  useEffect(() => {
    let isMounted = true;
    let pollInterval = null;

    const checkStateAndFetch = async () => {
      try {
        const statusRes = await getStatus(matchId);
        if (!isMounted) return;

        setStatus(statusRes.status);

        if (statusRes.status === 'completed') {
          const res = await getResults(matchId);
          if (!isMounted) return;
          setResults(res);
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        } else if (statusRes.status === 'failed') {
          setError(statusRes.error || 'Video analysis failed on server.');
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        }
      } catch (err) {
        if (!isMounted) return;
        setError(err.message || 'Error communicating with backend API.');
        setLoading(false);
        if (pollInterval) clearInterval(pollInterval);
      }
    };

    checkStateAndFetch();
    // Poll every 2 seconds while processing
    pollInterval = setInterval(checkStateAndFetch, 2000);

    return () => {
      isMounted = false;
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [matchId]);

  // Click-to-seek handler: directly sets video.currentTime to event.start_seconds and calls play()
  const handleSeek = (startSeconds, eventId) => {
    setActiveEventId(eventId);
    if (videoRef.current) {
      videoRef.current.currentTime = Number(startSeconds) || 0;
      videoRef.current.play().catch(() => {});
    }
  };

  const originalVideoSrc = initialVideoUrl || getMediaVideoUrl(matchId);
  const annotatedVideoSrc = getMediaAnnotatedUrl(matchId);
  const activeVideoSrc = videoMode === 'annotated' ? annotatedVideoSrc : originalVideoSrc;

  return (
    <div className="analysis-page-wrapper">
      {/* Top Header */}
      <div className="analysis-top-nav">
        <button type="button" className="btn-back-link" onClick={onBackToUpload}>
          <ArrowLeft className="nav-arrow-icon" /> Return to Video Upload
        </button>

        <div className="analysis-header-center">
          <h2 className="match-heading">Tactical Analysis #{matchId}</h2>
          <span className="sport-tag">Badminton (BWF Court)</span>
        </div>

        <div className="job-status-pill">
          {status === 'completed' ? (
            <span className="status-badge-done">
              <CheckCircle2 className="status-badge-icon" /> Analysis Completed
            </span>
          ) : status === 'failed' ? (
            <span className="status-badge-error">
              <AlertCircle className="status-badge-icon" /> Job Failed
            </span>
          ) : (
            <span className="status-badge-wait">
              <Loader2 className="status-badge-icon animate-spin" /> Processing AI Tracks...
            </span>
          )}
        </div>
      </div>

      {/* Warnings Banner */}
      {results?.warnings && results.warnings.length > 0 && (
        <div className="notice-box-warning">
          <AlertTriangle className="notice-icon" />
          <div className="notice-text">
            {results.warnings.map((w, idx) => (
              <p key={idx}>{w}</p>
            ))}
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="notice-box-error">
          <AlertCircle className="notice-icon" />
          <div className="notice-text">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {loading && !results ? (
        <div className="analysis-loading-state">
          <Loader2 className="loading-icon-large animate-spin text-primary" />
          <h3>Executing Badminton AI Pipeline</h3>
          <p>
            Running YOLOv8 person detection, multi-frame player tracking, and BWF court perspective projection...
          </p>
        </div>
      ) : results ? (
        <div className="analysis-content-body">
          {/* Main Area: Large Video Preview beside Court Heatmap */}
          <div className="visuals-primary-grid">
            {/* Left: Synchronized Video Player */}
            <div className="video-player-panel">
              <div className="panel-bar">
                <div className="panel-title-group">
                  <Video className="panel-icon text-primary" />
                  <span className="panel-title">Synchronized Replay</span>
                </div>

                <div className="player-mode-toggle">
                  <button
                    type="button"
                    className={`toggle-btn ${videoMode === 'annotated' ? 'active' : ''}`}
                    onClick={() => setVideoMode('annotated')}
                  >
                    AI Tracking View
                  </button>
                  <button
                    type="button"
                    className={`toggle-btn ${videoMode === 'original' ? 'active' : ''}`}
                    onClick={() => setVideoMode('original')}
                  >
                    Raw Footage
                  </button>
                </div>
              </div>

              <div className="video-frame-box">
                <video
                  ref={videoRef}
                  src={activeVideoSrc}
                  controls
                  playsInline
                  className="match-video-el"
                  onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)}
                  onError={() => {
                    if (videoMode === 'annotated') {
                      setVideoMode('original');
                    }
                  }}
                />
              </div>

              <div className="video-meta-footer">
                <span>Timestamp: {currentTime.toFixed(1)}s / {results.duration_seconds || 0}s</span>
                <span className="source-label">
                  {videoMode === 'annotated' ? 'YOLOv8 Multi-Frame Annotated' : 'Original Video Stream'}
                </span>
              </div>
            </div>

            {/* Right: BWF Court Heatmap & Trajectory */}
            <div className="court-visual-panel">
              <CourtHeatmap
                heatmap={results.heatmap}
                tracks={results.tracks}
              />
            </div>
          </div>

          {/* Metric Cards Row (Compact, rendered below main area) */}
          <section className="metrics-row-section">
            <h4 className="section-label">Movement Metrics</h4>
            <div className="metrics-cards-container">
              {results.metrics && results.metrics.length > 0 ? (
                results.metrics.map((m) => (
                  <MetricCard key={m.key} metric={m} />
                ))
              ) : (
                <div className="empty-state-text">No movement metrics available for this clip.</div>
              )}
            </div>
          </section>

          {/* Evidence List Below */}
          <section className="evidence-section">
            <EvidenceTimeline
              events={results.events || []}
              activeEventId={activeEventId}
              onSeekToEvent={handleSeek}
            />
          </section>
        </div>
      ) : null}
    </div>
  );
}
