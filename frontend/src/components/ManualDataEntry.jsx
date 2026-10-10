import React, { useState } from 'react';
import { PlusCircle, Tag, Check, Calendar, User, MapPin } from 'lucide-react';
import { addManualObservation } from '../api';

export default function ManualDataEntry({ matchId, currentTime = 0, onObservationAdded, existingObservations = [] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [eventType, setEventType] = useState('unforced_error');
  const [player, setPlayer] = useState(1);
  const [zone, setZone] = useState('Midcourt');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!notes.trim()) return;

    setSaving(true);
    setSuccessMsg(null);

    const payload = {
      timestamp_seconds: Number(currentTime.toFixed(2)),
      player_id: Number(player),
      event_type: eventType,
      notes: notes.trim(),
      court_zone: zone
    };

    try {
      await addManualObservation(matchId, payload);
      setNotes('');
      setSuccessMsg('Tactical observation tagged successfully!');
      if (onObservationAdded) {
        onObservationAdded(payload);
      }
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err) {
      alert(`Could not save observation: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="manual-entry-panel">
      <div className="manual-header-row">
        <div className="title-group">
          <Tag className="icon text-primary" />
          <h4 className="panel-title">Manual Tactical Annotation & Coach Tagging</h4>
        </div>
        <button
          type="button"
          className="btn-toggle-manual"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? 'Close Tagging Form' : '+ Add Manual Observation'}
        </button>
      </div>

      {isOpen && (
        <form onSubmit={handleSubmit} className="manual-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Current Video Timestamp</label>
              <input
                type="text"
                readOnly
                value={`${currentTime.toFixed(1)}s (Auto-synced)`}
                className="input-readonly"
              />
            </div>

            <div className="form-group">
              <label>Target Player</label>
              <select value={player} onChange={(e) => setPlayer(e.target.value)}>
                <option value={1}>Player 1</option>
                <option value={2}>Player 2</option>
              </select>
            </div>

            <div className="form-group">
              <label>Observation Category</label>
              <select value={eventType} onChange={(e) => setEventType(e.target.value)}>
                <option value="unforced_error">Unforced Error</option>
                <option value="smash_winner">Smash Winner</option>
                <option value="drop_shot_winner">Drop Shot Winner</option>
                <option value="poor_recovery">Delayed Recovery / Late Split-Step</option>
                <option value="tactical_exploit">Opponent Weakness Exploited</option>
                <option value="custom_note">Coach Observation Note</option>
              </select>
            </div>

            <div className="form-group">
              <label>Court Zone</label>
              <select value={zone} onChange={(e) => setZone(e.target.value)}>
                <option value="Forecourt">Forecourt (Net)</option>
                <option value="Midcourt">Midcourt / Sides</option>
                <option value="Rearcourt">Rearcourt (Baseline)</option>
              </select>
            </div>
          </div>

          <div className="form-group full-width">
            <label>Coach Notes & Tactical Context</label>
            <input
              type="text"
              placeholder="e.g. Crosscourt slice drop caught opponent moving wrong direction."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              required
              className="input-text"
            />
          </div>

          <div className="form-actions">
            <button type="submit" disabled={saving} className="btn-save-tag">
              {saving ? 'Saving...' : 'Save Observation to Match Report'}
            </button>
            {successMsg && <span className="save-success-msg"><Check className="inline-check" /> {successMsg}</span>}
          </div>
        </form>
      )}

      {/* Render list of existing manual observations */}
      {existingObservations && existingObservations.length > 0 && (
        <div className="manual-tags-list">
          <span className="tags-count-lbl">Logged Coach Annotations ({existingObservations.length}):</span>
          <div className="tags-chips-container">
            {existingObservations.map((obs, idx) => (
              <div key={idx} className="tag-chip">
                <span className="chip-time">{obs.timestamp_seconds}s</span>
                <span className="chip-type">P{obs.player_id} • {obs.event_type.replace('_', ' ')}</span>
                <span className="chip-zone">[{obs.court_zone}]</span>
                <span className="chip-notes">{obs.notes}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
