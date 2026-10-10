import React, { useState, useEffect } from 'react';
import { Clock, BarChart3, Activity, ArrowRight, RefreshCw } from 'lucide-react';
import { getMinuteChunks } from '../api';

export default function MinuteSummarizer({ matchId, durationSeconds, onSeekToChunk }) {
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!matchId) return;
    let isMounted = true;
    const fetchChunks = async () => {
      setLoading(true);
      try {
        const res = await getMinuteChunks(matchId);
        if (isMounted && res.chunks) {
          setChunks(res.chunks);
        }
      } catch (err) {
        console.warn('Could not load minute chunks:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchChunks();
    return () => { isMounted = false; };
  }, [matchId]);

  return (
    <div className="minute-summarizer-card">
      <div className="card-top-bar">
        <div className="title-group">
          <Clock className="icon text-primary" />
          <h4 className="panel-title">1-Minute Segment Breakdown & Clip Summaries</h4>
        </div>
        <span className="window-tag">{chunks.length} Segment{chunks.length !== 1 ? 's' : ''} Analyzed</span>
      </div>

      <div className="chunks-grid">
        {loading ? (
          <div className="loading-state-p"><RefreshCw className="animate-spin inline" /> Generating 1-minute tactical clip intervals...</div>
        ) : chunks.length === 0 ? (
          <div className="empty-state-p">No minute intervals available for this clip duration.</div>
        ) : (
          chunks.map((chk) => (
            <div key={chk.chunk_index} className="chunk-box">
              <div className="chunk-header">
                <span className="chunk-badge">Clip Interval {chk.chunk_index}</span>
                <span className="chunk-time">{chk.time_range}</span>
              </div>

              <div className="chunk-meta">
                <span className="intensity-pill">{chk.intensity}</span>
                <span className="samples-lbl">{chk.samples_count} track samples</span>
              </div>

              <p className="chunk-summary-text">{chk.summary}</p>

              <div className="chunk-zone-footer">
                <span className="zone-lbl">Active Zone:</span> <span>{chk.dominant_zone}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
