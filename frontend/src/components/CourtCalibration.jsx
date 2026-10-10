import React, { useState, useRef, useEffect } from 'react';
import { Target, RotateCcw, Undo2, CheckCircle2, Info } from 'lucide-react';

const CORNER_NAMES = [
  '1. Top-Left',
  '2. Top-Right',
  '3. Bottom-Right',
  '4. Bottom-Left'
];

export default function CourtCalibration({ videoUrl, onCornersConfirmed, initialCourtType = 'doubles' }) {
  const [corners, setCorners] = useState([]); // Array of [sourceX, sourceY]
  const [displayCorners, setDisplayCorners] = useState([]); // Array of [dispX, dispY] for visual overlay
  const [courtType, setCourtType] = useState(initialCourtType);
  const [videoDims, setVideoDims] = useState({ width: 0, height: 0 });

  const videoRef = useRef(null);
  const containerRef = useRef(null);

  const handleVideoLoaded = () => {
    if (videoRef.current) {
      setVideoDims({
        width: videoRef.current.videoWidth || 1280,
        height: videoRef.current.videoHeight || 720
      });
    }
  };

  const handleContainerClick = (e) => {
    if (corners.length >= 4) return;
    if (!videoRef.current || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const clickDispX = e.clientX - rect.left;
    const clickDispY = e.clientY - rect.top;

    const containerWidth = rect.width;
    const containerHeight = rect.height;

    const srcWidth = videoDims.width || videoRef.current.videoWidth || containerWidth;
    const srcHeight = videoDims.height || videoRef.current.videoHeight || containerHeight;

    // Account for object-fit: contain letterboxing
    const videoAspect = srcWidth / srcHeight;
    const containerAspect = containerWidth / containerHeight;

    let renderWidth = containerWidth;
    let renderHeight = containerHeight;
    let offsetX = 0;
    let offsetY = 0;

    if (containerAspect > videoAspect) {
      renderHeight = containerHeight;
      renderWidth = containerHeight * videoAspect;
      offsetX = (containerWidth - renderWidth) / 2;
    } else {
      renderWidth = containerWidth;
      renderHeight = containerWidth / videoAspect;
      offsetY = (containerHeight - renderHeight) / 2;
    }

    const relX = clickDispX - offsetX;
    const relY = clickDispY - offsetY;

    if (relX < 0 || relX > renderWidth || relY < 0 || relY > renderHeight) {
      return; // Ignore clicks in letterbox margins
    }

    const scaleX = srcWidth / renderWidth;
    const scaleY = srcHeight / renderHeight;

    const scaledX = Math.round(relX * scaleX);
    const scaledY = Math.round(relY * scaleY);

    const newCorners = [...corners, [scaledX, scaledY]];
    const newDisplayCorners = [...displayCorners, [clickDispX, clickDispY]];

    setCorners(newCorners);
    setDisplayCorners(newDisplayCorners);

    if (newCorners.length === 4) {
      onCornersConfirmed({
        corners: newCorners,
        courtType: courtType
      });
    }
  };

  const handleUndo = () => {
    if (corners.length > 0) {
      const updatedCorners = corners.slice(0, -1);
      setCorners(updatedCorners);
      setDisplayCorners(displayCorners.slice(0, -1));
      onCornersConfirmed({
        corners: updatedCorners.length === 4 ? updatedCorners : null,
        courtType: courtType
      });
    }
  };

  const handleReset = () => {
    setCorners([]);
    setDisplayCorners([]);
    onCornersConfirmed({
      corners: null,
      courtType: courtType
    });
  };

  const handleCourtTypeChange = (newType) => {
    setCourtType(newType);
    if (corners.length === 4) {
      onCornersConfirmed({
        corners: corners,
        courtType: newType
      });
    }
  };

  const isComplete = corners.length === 4;
  const currentStep = isComplete ? 'Complete' : CORNER_NAMES[corners.length];

  return (
    <div className="calibration-box">
      <div className="calibration-header">
        <div className="calibration-title-row">
          <Target className="title-icon text-primary" />
          <h3 className="calib-title">Court Calibration</h3>
          <span className={`status-tag ${isComplete ? 'tag-complete' : 'tag-active'}`}>
            {isComplete ? '4/4 Corners Selected' : `Step ${corners.length + 1}/4: Click ${currentStep}`}
          </span>
        </div>

        <div className="calib-controls">
          <select
            className="calib-select"
            value={courtType}
            onChange={(e) => handleCourtTypeChange(e.target.value)}
          >
            <option value="doubles">🏸 Doubles Court (6.10m)</option>
            <option value="singles">🏸 Singles Court (5.18m)</option>
          </select>

          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={handleUndo}
            disabled={corners.length === 0}
            title="Undo last point"
          >
            <Undo2 className="btn-icon-sm" /> Undo
          </button>

          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={handleReset}
            disabled={corners.length === 0}
            title="Reset all points"
          >
            <RotateCcw className="btn-icon-sm" /> Reset
          </button>
        </div>
      </div>

      <div className="calib-guide">
        <Info className="guide-icon" />
        <span>
          Click the 4 corners of the court in order: <strong>Top-Left → Top-Right → Bottom-Right → Bottom-Left</strong>.
          Coordinates are automatically scaled to source resolution ({videoDims.width}×{videoDims.height}px).
        </span>
      </div>

      {/* Interactive Video Frame Overlay */}
      <div
        ref={containerRef}
        className={`calib-viewport ${!isComplete ? 'cursor-crosshair' : ''}`}
        onClick={handleContainerClick}
      >
        <video
          ref={videoRef}
          src={videoUrl}
          playsInline
          muted
          className="calib-video"
          onLoadedMetadata={handleVideoLoaded}
        />

        {/* SVG Overlay for Points and Polygon Lines */}
        <svg className="calib-svg-overlay">
          {displayCorners.length >= 2 && (
            <polyline
              points={displayCorners.map(([x, y]) => `${x},${y}`).join(' ')}
              className="calib-polyline"
            />
          )}

          {isComplete && (
            <polygon
              points={displayCorners.map(([x, y]) => `${x},${y}`).join(' ')}
              className="calib-polygon-closed"
            />
          )}

          {displayCorners.map(([x, y], idx) => (
            <g key={idx} transform={`translate(${x}, ${y})`}>
              <circle r="9" className="calib-point-circle" />
              <text textAnchor="middle" dy="4" className="calib-point-text">
                {idx + 1}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {/* Selected Coordinates Inspector */}
      <div className="calib-coords-tray">
        {CORNER_NAMES.map((name, idx) => {
          const pt = corners[idx];
          return (
            <div key={idx} className={`coord-chip ${pt ? 'filled' : 'empty'}`}>
              <span className="chip-label">{name}:</span>
              <span className="chip-val">{pt ? `[${pt[0]}, ${pt[1]}]` : 'Pending click'}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
