# RallyLens AI — Badminton Tactical Intelligence (Sprint: Hours 12–13)

**Mission**: Stop expanding scope. Stabilize the actual badminton video-to-report workflow, validate the output, and prepare a repeatable judge demo.

---

## 👥 Hours 12–13 Member Ownership & Deliverables

| Member | Role | Owned Files | Hours 12–13 Release Verification |
| :--- | :--- | :--- | :--- |
| **Member 1** | **AI Lead** | `backend/app/vision/tracking.py`<br>`backend/app/vision/metrics.py`<br>`backend/app/vision/evidence.py`<br>`backend/app/vision/video.py`<br>`backend/data/results/validation_notes.md` | ✅ **PASS**<br>• Runs target clip through tracking from a clean start.<br>• Filtered jumps, persistent player IDs, monotonic timestamps.<br>• Automated warnings when calibration or tracking density is limited.<br>• Generates **Rally Evidence Loop** with measured repositioning patterns and defensible coaching suggestions.<br>• Authored 20-second limitations statement for judges. |
| **Member 2** | **Frontend Upload Lead** | `frontend/src/components/VideoUpload.jsx`<br>`frontend/src/components/CourtCalibration.jsx`<br>`frontend/src/pages/Home.jsx`<br>`frontend/src/api.js` | ✅ **PASS**<br>• Upload success and unsupported/corrupt file rejection verified.<br>• Court calibration accounts for display scaling and `object-fit: contain` letterboxing to map original video coordinates.<br>• Clean handling of upload, processing, completed, and failed states.<br>• Non-blocking retry without page reload. |
| **Member 3** | **Results Dashboard Lead** | `frontend/src/pages/Analysis.jsx`<br>`frontend/src/components/MetricCard.jsx`<br>`frontend/src/components/CourtHeatmap.jsx`<br>`frontend/src/components/EvidenceTimeline.jsx` | ✅ **PASS**<br>• Clean sports-analytics SaaS theme (no fake AI effects / glow).<br>• Real report screen displays API results; uncalibrated metrics show "Not available" + explicit reason.<br>• Heatmap includes visual density swatches and player track legend.<br>• Click-to-seek discovery seeks video directly to event start timestamp. |
| **Member 4** | **Backend API Lead** | `backend/app/main.py`<br>`backend/app/schemas.py`<br>`backend/app/jobs.py`<br>`backend/app/sports.py`<br>`.gitignore` | ✅ **PASS**<br>• Consistent match ID and job status lifecycle.<br>• Guaranteed: jobs cannot be returned as completed before results exist (returns HTTP 409 if unready).<br>• Saved result retrieval from disk without re-inference.<br>• Media streaming (`/media/{id}/video`, `/media/{id}/annotated.mp4`) with ID traversal protection.<br>• Local offline presentation backup in `backend/data/results/backup_demo/`. |

---

## 🎯 Hours 12–13 Acceptance Tests Matrix

| Test | Pass Criterion | Status |
| :--- | :--- | :---: |
| **1. Video upload** | Valid clip is accepted with stable ID; invalid input shows useful error. | **PASS** |
| **2. Court calibration** | 4 selected corners match boundaries, correct order, transform positions consistently. | **PASS** |
| **3. Player tracking** | Players detected across frames; obvious switches & missing segments inspected. | **PASS** |
| **4. Metric sanity** | Distance and coverage use valid court coordinates; values plausible. | **PASS** |
| **5. Results authenticity** | No placeholder values appear as actual results. Unavailable metrics shown as unavailable. | **PASS** |
| **6. Evidence replay** | Selected event plays correct source video at expected start time. | **PASS** |
| **7. Failure handling** | Processing failure changes status to failed and displays visible, actionable message. | **PASS** |
| **8. Repeatability** | Complete end-to-end flow succeeds twice consecutively; backup fixture ready. | **PASS** |

---

## 🎤 Five-Minute Judge Walkthrough Script

| Time | Show | Say |
| :--- | :--- | :--- |
| **0:00 - 0:35** | **Problem and upload** | *"We turn a normal badminton recording into accessible movement analysis without specialized tracking hardware."* |
| **0:35 - 1:20** | **Court calibration and tracking overlay** | *"Show real detected players and how the court is mapped. State the limits of the selected camera view."* |
| **1:20 - 2:20** | **Metrics and heatmap** | *"Explain the three actual metrics, their units, and how they come from valid tracked positions."* |
| **2:20 - 3:20** | **Evidence click and replay** | *"Click a real movement event and replay the relevant timestamp; show that the metric is traceable to video evidence."* |
| **3:20 - 4:15** | **Confidence / limitation** | *"Explain how poor detections are flagged rather than presented as facts."* |
| **4:15 - 5:00** | **Cross-sport path and impact** | *"Show the configurable architecture and explain that other sports require sport-specific validation."* |

---

## 🚀 Running the Application

### 1. Start Backend API (Port 8000)
```powershell
.\run_backend.bat
```
*(Interactive API Docs: `http://localhost:8000/docs`)*

### 2. Start Frontend UI (Port 5173)
```powershell
.\run_frontend.bat
```
*(Web Application: `http://localhost:5173` — Enter Match ID `backup_demo` for immediate offline replay)*

---

## 🧪 Automated Verification Suite
Run the full sprint test suite:
```powershell
cd backend
.\.venv\Scripts\python.exe test_hour_12_13_sprint.py
```

---

## 🏆 Final Team Decision
**Status**: **Demo-ready** (All critical acceptance tests pass, video-to-report flow succeeds repeatedly, and local backup assets are verified).
