import React, { useState, useRef, useEffect } from 'react';
import { Upload, Film, Play, AlertCircle, AlertTriangle, CheckCircle, Loader2, RefreshCw, Camera, Video, StopCircle } from 'lucide-react';
import { uploadMatch, startAnalysis } from '../api';
import CourtCalibration from './CourtCalibration';

const ACCEPTED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.webm', '.mkv'];
const MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024; // 200 MB

export default function VideoUpload({ onAnalysisStarted, onUseSample }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [sport, setSport] = useState('badminton');
  const [courtType, setCourtType] = useState('doubles');
  const [courtCorners, setCourtCorners] = useState(null);

  const [uploadStatus, setUploadStatus] = useState('idle'); // idle | uploading | uploaded | analyzing | error
  const [matchId, setMatchId] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [calibWarning, setCalibWarning] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [reopenId, setReopenId] = useState('');

  // Real-time camera recording states
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const streamRef = useRef(null);
  const liveVideoPreviewRef = useRef(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileSelection = async (file) => {
    if (!file) return;

    // 1. File size check
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorMessage(`File is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum allowed size is 200 MB.`);
      setUploadStatus('error');
      return;
    }

    // 2. Extension check
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ACCEPTED_EXTENSIONS.includes(ext)) {
      setErrorMessage(`Unsupported video format "${ext}". Supported formats: MP4, MOV, AVI, WebM.`);
      setUploadStatus('error');
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const objectUrl = URL.createObjectURL(file);
    setSelectedFile(file);
    setPreviewUrl(objectUrl);
    setErrorMessage(null);
    setCalibWarning(null);
    setCourtCorners(null);

    // Upload to FastAPI backend
    try {
      setUploadStatus('uploading');
      const res = await uploadMatch(file);
      setMatchId(res.match_id);
      setUploadStatus('uploaded');
    } catch (err) {
      setUploadStatus('error');
      setErrorMessage(err.message || 'Video upload failed. Check backend connection.');
    }
  };

  // Real-time camera recording logic (works with laptop webcam or mobile browser back camera)
  const startCameraRecording = async () => {
    try {
      setErrorMessage(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      streamRef.current = stream;
      if (liveVideoPreviewRef.current) {
        liveVideoPreviewRef.current.srcObject = stream;
      }

      recordedChunksRef.current = [];
      const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
        ? 'video/webm;codecs=vp9'
        : 'video/webm';

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        const capturedFile = new File([blob], `live_badminton_${Date.now()}.webm`, { type: 'video/webm' });
        // Stop stream tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
        }
        setIsRecording(false);
        handleFileSelection(capturedFile);
      };

      recorder.start(1000); // 1-second chunks
      setIsRecording(true);
      setRecordingSeconds(0);
    } catch (err) {
      setErrorMessage(`Camera access denied or unavailable: ${err.message}`);
    }
  };

  const stopCameraRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  useEffect(() => {
    let timer = null;
    if (isRecording) {
      timer = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => { if (timer) clearInterval(timer); };
  }, [isRecording]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleCornersConfirmed = ({ corners, courtType: cType }) => {
    setCourtCorners(corners);
    if (cType) setCourtType(cType);
    if (corners && corners.length === 4) {
      setCalibWarning(null);
    }
  };

  const handleStartAnalysis = async () => {
    if (!matchId) {
      setErrorMessage('Please select and upload a video file first.');
      return;
    }

    if (!courtCorners || courtCorners.length < 4) {
      setCalibWarning(
        'Court calibration not completed: Distance in metres will be null and uncalibrated pixel coordinates will be used.'
      );
    }

    try {
      setErrorMessage(null);
      setUploadStatus('analyzing');

      await startAnalysis(matchId, {
        sport,
        court_type: courtType,
        court_corners: courtCorners && courtCorners.length === 4 ? courtCorners : null
      });

      if (onAnalysisStarted) {
        onAnalysisStarted({
          matchId,
          filename: selectedFile ? selectedFile.name : 'clip.mp4',
          previewUrl,
          sport,
          courtType,
          courtCorners
        });
      }
    } catch (err) {
      setUploadStatus('error');
      setErrorMessage(err.message || 'Failed to trigger video analysis.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  return (
    <div className="upload-container">
      <div className="card upload-card">
        <h2 className="card-title">
          <Film className="title-icon text-primary" />
          Badminton Match Video Upload
        </h2>
        <p className="card-subtitle">
          Upload recorded footage to extract player tracks, court coverage, and tactical evidence.
        </p>

        {/* Dropzone */}
        <div
          className={`dropzone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !previewUrl && fileInputRef.current && fileInputRef.current.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />

          {!previewUrl ? (
            <div className="dropzone-prompt">
              {isRecording ? (
                <div className="live-camera-recording-box" onClick={(e) => e.stopPropagation()}>
                  <video
                    ref={liveVideoPreviewRef}
                    autoPlay
                    playsInline
                    muted
                    className="live-camera-video-feed"
                  />
                  <div className="recording-indicator-row">
                    <span className="rec-pulse-dot"></span>
                    <span className="rec-timer-text">Recording Live Court Footage: {recordingSeconds}s</span>
                  </div>
                  <button
                    type="button"
                    className="btn btn-danger btn-stop-rec"
                    onClick={stopCameraRecording}
                  >
                    <StopCircle className="btn-icon" /> Stop & Process Clip
                  </button>
                </div>
              ) : (
                <>
                  <div className="upload-icon-wrapper">
                    <Upload className="upload-icon" />
                  </div>
                  <p className="drop-main-text">
                    <strong>Click to browse</strong> or drag & drop video here
                  </p>
                  <p className="drop-sub-text">MP4, MOV, AVI, or WebM (Max 200MB)</p>

                  <div className="camera-record-row" onClick={(e) => e.stopPropagation()}>
                    <span className="divider-text">── OR ──</span>
                    <button
                      type="button"
                      className="btn-camera-capture"
                      onClick={startCameraRecording}
                    >
                      <Camera className="camera-icon" /> Record Live with Mobile / Webcam
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="preview-wrapper" onClick={(e) => e.stopPropagation()}>
              <div className="file-meta-bar">
                <div className="file-meta-left">
                  <span className="file-name" title={selectedFile?.name}>
                    {selectedFile?.name}
                  </span>
                  <span className="file-size">{formatFileSize(selectedFile?.size)}</span>
                </div>

                <div className="file-meta-right">
                  {matchId && (
                    <span className="match-pill">
                      <CheckCircle className="pill-icon-sm" /> Match ID: #{matchId}
                    </span>
                  )}
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  >
                    <RefreshCw className="btn-icon-sm" /> Change Video
                  </button>
                </div>
              </div>

              {/* Court Calibration Step */}
              <CourtCalibration
                videoUrl={previewUrl}
                onCornersConfirmed={handleCornersConfirmed}
                initialCourtType={courtType}
              />
            </div>
          )}
        </div>

        {/* Options Grid */}
        <div className="options-grid">
          <div className="form-group">
            <label className="form-label" htmlFor="sport-selector">Target Sport</label>
            <select
              id="sport-selector"
              className="form-select"
              value={sport}
              onChange={(e) => setSport(e.target.value)}
              disabled={uploadStatus === 'analyzing'}
            >
              <option value="badminton">🏸 Badminton (BWF - Active)</option>
              <option value="tennis" disabled>🎾 Tennis (Architecture Roadmap)</option>
              <option value="squash" disabled>👟 Squash (Architecture Roadmap)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Calibration State</label>
            <div className="engine-badge">
              {courtCorners && courtCorners.length === 4 ? (
                <span className="badge-calibrated">
                  <CheckCircle className="pill-icon-sm text-emerald" /> 4 Corners Calibrated (Metres active)
                </span>
              ) : (
                <span className="badge-uncalibrated">
                  ⚠️ Uncalibrated (Distance in metres will be null)
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Calibration Warning */}
        {calibWarning && (
          <div className="notice-box-warning">
            <AlertTriangle className="notice-icon" />
            <div className="notice-text">
              <strong>Notice:</strong> {calibWarning}
            </div>
          </div>
        )}

        {/* Error message */}
        {errorMessage && (
          <div className="notice-box-error">
            <AlertCircle className="notice-icon" />
            <div className="notice-text">
              <strong>Error:</strong> {errorMessage}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="actions-bar">
          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={handleStartAnalysis}
            disabled={!matchId || uploadStatus === 'uploading' || uploadStatus === 'analyzing'}
          >
            {uploadStatus === 'uploading' ? (
              <>
                <Loader2 className="btn-icon animate-spin" /> Uploading Video...
              </>
            ) : uploadStatus === 'analyzing' ? (
              <>
                <Loader2 className="btn-icon animate-spin" /> Starting AI Analysis...
              </>
            ) : (
              <>
                <Play className="btn-icon fill-current" /> Analyze Badminton Match
              </>
            )}
          </button>

          {onUseSample && (
            <button
              type="button"
              className="btn btn-outline"
              onClick={onUseSample}
              disabled={uploadStatus === 'analyzing'}
            >
              ⚡ Load Presentation Backup
            </button>
          )}
        </div>

        {/* Reopen Existing Report without rerunning analysis */}
        <div className="reopen-tray">
          <span className="reopen-label">Or reopen saved report:</span>
          <div className="reopen-input-group">
            <input
              type="text"
              placeholder="Enter Match ID (e.g. backup_demo)"
              className="reopen-input"
              value={reopenId}
              onChange={(e) => setReopenId(e.target.value.trim())}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && reopenId) {
                  onAnalysisStarted({ matchId: reopenId, filename: `${reopenId}.mp4`, sport: 'badminton' });
                }
              }}
            />
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={!reopenId}
              onClick={() => {
                if (reopenId) {
                  onAnalysisStarted({ matchId: reopenId, filename: `${reopenId}.mp4`, sport: 'badminton' });
                }
              }}
            >
              Open Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
