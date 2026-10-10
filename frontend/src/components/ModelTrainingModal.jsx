import React, { useState, useEffect } from 'react';
import { Database, Play, CheckCircle2, Loader2, BookOpen, Layers, ShieldCheck } from 'lucide-react';
import { startTraining, getTrainingStatus } from '../api';

const DATASETS = [
  {
    id: 'BFMD',
    name: 'BFMD (Badminton-Focused Multi-Task Dataset)',
    description: 'High-density broadcast and court camera annotations for player bounding boxes, pose, and court corner landmarks.',
    recommendedEpochs: 15,
    sampleCount: '12,400 annotated frames'
  },
  {
    id: 'Shuttlecock Trajectory Dataset',
    name: 'Shuttlecock Trajectory Dataset',
    description: 'Specialized 2D/3D high-speed badminton ball & shuttle flight path coordinate sequences across professional rallies.',
    recommendedEpochs: 20,
    sampleCount: '28,500 labeled trajectory points'
  },
  {
    id: 'SportsMOT',
    name: 'SportsMOT (Sports Multi-Object Tracking)',
    description: 'Complex court multi-target tracking benchmarks designed to minimize identity switches under rapid athlete crossovers.',
    recommendedEpochs: 12,
    sampleCount: '45,000 player tracks'
  }
];

export default function ModelTrainingModal({ onClose }) {
  const [selectedDataset, setSelectedDataset] = useState('BFMD');
  const [epochs, setEpochs] = useState(10);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let interval = null;
    if (job && job.status === 'training') {
      interval = setInterval(async () => {
        try {
          const res = await getTrainingStatus(job.job_id);
          setJob(res);
          if (res.status === 'completed') {
            clearInterval(interval);
          }
        } catch (e) {
          console.error(e);
        }
      }, 1000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [job]);

  const handleLaunchTraining = async () => {
    setLoading(true);
    try {
      const res = await startTraining(selectedDataset, epochs);
      setJob(res);
    } catch (err) {
      alert(`Could not start training: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="training-modal-box">
        <div className="modal-header">
          <div className="title-group">
            <Database className="icon text-primary" />
            <h3>Fine-Tune Vision Pipeline on Sports Datasets</h3>
          </div>
          <button type="button" className="btn-close" onClick={onClose}>&times;</button>
        </div>

        <p className="modal-subtitle">
          Select curated racket sports datasets to train and adapt YOLOv8 weights for specialized badminton player detection and tracking.
        </p>

        {/* Datasets selector */}
        <div className="dataset-cards-grid">
          {DATASETS.map((ds) => (
            <div
              key={ds.id}
              className={`dataset-card ${selectedDataset === ds.id ? 'active' : ''}`}
              onClick={() => setSelectedDataset(ds.id)}
            >
              <div className="card-top">
                <span className="dataset-id">{ds.id}</span>
                <span className="dataset-samples">{ds.sampleCount}</span>
              </div>
              <h4 className="dataset-name">{ds.name}</h4>
              <p className="dataset-desc">{ds.description}</p>
            </div>
          ))}
        </div>

        {/* Training Parameters */}
        <div className="training-params-row">
          <div className="param-item">
            <label>Training Epochs</label>
            <input
              type="number"
              min="5"
              max="50"
              value={epochs}
              onChange={(e) => setEpochs(Number(e.target.value) || 10)}
            />
          </div>
          <div className="param-item">
            <label>Pretrained Backbone</label>
            <input type="text" readOnly value="yolov8n.pt (COCO Person Class 0)" />
          </div>
          <div className="param-item">
            <label>Optimization Target</label>
            <input type="text" readOnly value="mAP@0.50 & ByteTrack Consistency" />
          </div>
        </div>

        {/* Launch button */}
        {!job ? (
          <div className="modal-actions">
            <button
              type="button"
              className="btn-start-train"
              disabled={loading}
              onClick={handleLaunchTraining}
            >
              {loading ? <Loader2 className="animate-spin inline" /> : <Play className="inline-play" />}
              Start Transfer Learning on {selectedDataset}
            </button>
          </div>
        ) : (
          <div className="training-progress-panel">
            <div className="progress-top-info">
              <span>Status: <strong>{job.status.toUpperCase()}</strong></span>
              <span>Epoch: <strong>{job.current_epoch} / {job.total_epochs}</strong></span>
              <span>Current mAP@0.50: <strong>{job.current_map50}</strong></span>
            </div>

            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${job.progress}%` }}
              />
            </div>

            <div className="training-console">
              <pre>{job.log_output}</pre>
            </div>

            {job.status === 'completed' && (
              <div className="completion-banner">
                <CheckCircle2 className="icon-success" />
                <span>Fine-tuned weights successfully saved! Model is ready for court inference.</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
