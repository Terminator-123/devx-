import React from 'react';
import { Activity, Gauge, MapPin, Layers, AlertCircle } from 'lucide-react';

const ICON_MAP = {
  distance_m: MapPin,
  court_coverage: Activity,
  rear_court_dist: Gauge,
  tracked_samples: Layers,
  active_players: Layers,
};

export default function MetricCard({ metric }) {
  if (!metric) return null;

  const { key, label, value, unit, quality, confidence } = metric;
  const IconComponent = ICON_MAP[key] || Activity;

  const isNullValue = value === null || value === undefined;
  const isUncalibrated = quality === 'uncalibrated' || isNullValue;

  return (
    <div className={`clean-metric-card ${isUncalibrated ? 'card-uncalibrated' : ''}`}>
      <div className="clean-metric-header">
        <div className="clean-metric-label-group">
          <IconComponent className="clean-metric-icon" />
          <span className="clean-metric-label">{label}</span>
        </div>

        {quality && (
          <span className={`quality-badge ${isUncalibrated ? 'badge-warn' : 'badge-subtle'}`}>
            {quality}
          </span>
        )}
      </div>

      <div className="clean-metric-value-row">
        {isNullValue ? (
          <div className="clean-metric-unavailable">
            <span className="clean-metric-null">Not available</span>
            <span className="null-reason">Requires metric court calibration</span>
          </div>
        ) : (
          <>
            <span className="clean-metric-num">{value}</span>
            <span className="clean-metric-unit">{unit}</span>
          </>
        )}
      </div>

      {confidence !== undefined && confidence !== null && (
        <div className="clean-metric-conf">
          <span>Observed Confidence: {Math.round(confidence * 100)}%</span>
        </div>
      )}
    </div>
  );
}
