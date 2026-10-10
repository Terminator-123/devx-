import React, { useState } from 'react';
import { Layers, AlertCircle } from 'lucide-react';

export default function CourtHeatmap({ heatmap = null, tracks = [] }) {
  const [activePlayer, setActivePlayer] = useState('all');

  const heatmapCells = Array.isArray(heatmap) ? heatmap : (heatmap?.cells || []);
  const gridWidth = heatmap?.width || 10;
  const gridHeight = heatmap?.height || 5;

  // Flatten and filter track samples, keeping points strictly within court bounds [0..1]
  const validSamples = [];
  let uncalibratedCount = 0;

  if (Array.isArray(tracks)) {
    tracks.forEach((track) => {
      const pid = track.player_id;
      if (activePlayer === 'all' || String(pid) === String(activePlayer)) {
        (track.samples || []).forEach((s) => {
          if (s.calibration_valid && s.court_x !== null && s.court_y !== null) {
            // Keep strictly bounded 0..1
            if (s.court_x >= 0.0 && s.court_x <= 1.0 && s.court_y >= 0.0 && s.court_y <= 1.0) {
              validSamples.push({
                player_id: pid,
                x: s.court_x,
                y: s.court_y,
                timestamp: s.timestamp_seconds
              });
            }
          } else {
            uncalibratedCount++;
          }
        });
      }
    });
  }

  const isCalibrated = validSamples.length > 0;
  const maxHeat = heatmapCells.reduce((m, c) => Math.max(m, c.count || 0), 1);

  const getCellFill = (count) => {
    const ratio = Math.min(1, count / maxHeat);
    if (ratio > 0.7) return 'rgba(239, 68, 68, 0.65)';
    if (ratio > 0.4) return 'rgba(245, 158, 11, 0.50)';
    return 'rgba(37, 99, 235, 0.35)';
  };

  return (
    <div className="court-card-panel">
      <div className="court-header-row">
        <div className="court-title-group">
          <Layers className="court-icon text-primary" />
          <h4 className="court-title">BWF Court Heatmap</h4>
        </div>

        <div className="court-tabs">
          <button
            type="button"
            className={`court-tab ${activePlayer === 'all' ? 'active' : ''}`}
            onClick={() => setActivePlayer('all')}
          >
            All Players
          </button>
          <button
            type="button"
            className={`court-tab ${activePlayer === '1' ? 'active' : ''}`}
            onClick={() => setActivePlayer('1')}
          >
            Player 1
          </button>
          <button
            type="button"
            className={`court-tab ${activePlayer === '2' ? 'active' : ''}`}
            onClick={() => setActivePlayer('2')}
          >
            Player 2
          </button>
        </div>
      </div>

      {/* SVG Court Visualization */}
      <div className="court-svg-container">
        <svg viewBox="0 0 320 580" className="court-svg-canvas">
          {/* Surface */}
          <rect x="20" y="20" width="280" height="540" rx="3" className="court-surface" />

          {/* Doubles outer boundary */}
          <rect x="20" y="20" width="280" height="540" className="court-stroke outer-bound" />

          {/* Singles sidelines */}
          <line x1="40" y1="20" x2="40" y2="560" className="court-stroke inner-line" />
          <line x1="280" y1="20" x2="280" y2="560" className="court-stroke inner-line" />

          {/* Long service lines */}
          <line x1="20" y1="42" x2="300" y2="42" className="court-stroke inner-line" />
          <line x1="20" y1="538" x2="300" y2="538" className="court-stroke inner-line" />

          {/* Short service lines */}
          <line x1="20" y1="210" x2="300" y2="210" className="court-stroke inner-line" />
          <line x1="20" y1="370" x2="300" y2="370" className="court-stroke inner-line" />

          {/* Center service lines */}
          <line x1="160" y1="20" x2="160" y2="210" className="court-stroke inner-line" />
          <line x1="160" y1="370" x2="160" y2="560" className="court-stroke inner-line" />

          {/* Net */}
          <line x1="12" y1="290" x2="308" y2="290" className="court-net-line" />
          <line x1="12" y1="290" x2="308" y2="290" className="court-net-pattern" strokeDasharray="3,3" />

          {/* Render Heatmap Cells */}
          {heatmapCells.map((cell, idx) => {
            const cellW = 280 / gridWidth;
            const cellH = 540 / gridHeight;
            const x = 20 + cell.x * cellW;
            const y = 20 + cell.y * cellH;

            return (
              <rect
                key={`cell-${idx}`}
                x={x + 1}
                y={y + 1}
                width={cellW - 2}
                height={cellH - 2}
                rx={2}
                fill={getCellFill(cell.count || 0)}
              >
                <title>{`Zone (${cell.x}, ${cell.y}): ${cell.count} observations`}</title>
              </rect>
            );
          })}

          {/* Render Calibrated Player Trajectory Points */}
          {validSamples.map((pt, idx) => {
            const px = 20 + pt.x * 280;
            const py = 20 + pt.y * 540;
            const isP1 = pt.player_id === 1;

            return (
              <circle
                key={`pt-${idx}`}
                cx={px}
                cy={py}
                r="3.5"
                fill={isP1 ? '#10b981' : '#2563eb'}
                stroke="#ffffff"
                strokeWidth="0.8"
                opacity="0.85"
              >
                <title>{`Player ${pt.player_id} at ${pt.timestamp}s`}</title>
              </circle>
            );
          })}
        </svg>
      </div>

      {/* Visual Heatmap & Trajectory Legend */}
      <div className="court-legend-row">
        <div className="legend-group">
          <span className="legend-label">Density:</span>
          <span className="legend-swatch low"></span> Low
          <span className="legend-swatch med"></span> Mid
          <span className="legend-swatch high"></span> High
        </div>
        <div className="legend-group">
          <span className="legend-swatch p1"></span> P1
          <span className="legend-swatch p2"></span> P2
        </div>
      </div>

      <div className="court-caption">
        {isCalibrated ? (
          <span>{validSamples.length} perspective-mapped trajectory points rendered</span>
        ) : (
          <span className="uncalib-note">
            <AlertCircle className="note-icon" /> Court uncalibrated: top-down projection omitted.
          </span>
        )}
      </div>
    </div>
  );
}
