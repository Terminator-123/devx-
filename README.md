# RallyLens AI — Badminton Tactical Intelligence (Sprint: Hours 10–11)

A reliable, reproducible computer vision and tactical sports analysis engine built for recorded badminton video. Features CPU-first YOLOv8 person detection, 4-corner perspective calibration with letterbox compensation, deterministic multi-frame tracking, truthful metrics, and evidence-linked video replay.

---

## 👥 Hours 10–11 Release Member Ownership & Deliverables

| Member | Role | Owned Files | Hours 10–11 Release Verification |
| :--- | :--- | :--- | :--- |
| **Member 1** | **AI Lead** | `backend/app/vision/tracking.py`<br>`backend/app/vision/metrics.py`<br>`backend/app/vision/evidence.py`<br>`backend/app/vision/video.py`<br>`backend/data/results/validation_notes.md` | ✅ **PASS**<br>• Runs 30–60s video end-to-end.<br>• Filtered jumps, handled missing detections, verified units, and omitted metrics when uncalibrated.<br>• Generates **Rally Evidence Loop**: measured movement patterns linked to original video timestamps with cautious coaching suggestions.<br>• Prepared 20-second limitations statement for judges. |
| **Member 2** | **Frontend Upload Lead** | `frontend/src/components/VideoUpload.jsx`<br>`frontend/src/components/CourtCalibration.jsx`<br>`frontend/src/pages/Home.jsx`<br>`frontend/src/api.js` | ✅ **PASS**<br>• First-run flow tested: select video, confirm badminton, mark 4 corners, start analysis.<br>• Original-video coordinate scaling with aspect-ratio letterbox compensation.<br>• Actionable error messages and retry without page reload. |
| **Member 3** | **Results Dashboard Lead** | `frontend/src/pages/Analysis.jsx`<br>`frontend/src/components/MetricCard.jsx`<br>`frontend/src/components/CourtHeatmap.jsx`<br>`frontend/src/components/EvidenceTimeline.jsx` | ✅ **PASS**<br>• Clean sports-analytics SaaS theme (no neon glow/fake AI effects).<br>• Real report screen displays API results, units, and explicit reasons for uncalibrated metrics.<br>• Interactive Evidence Timeline with click-to-seek, measured patterns, and coaching suggestions.<br>• Empty arrays, failure states, and original/annotated toggle cleanly handled. |
| **Member 4** | **Backend API Lead** | `backend/app/main.py`<br>`backend/app/schemas.py`<br>`backend/app/jobs.py`<br>`backend/app/sports.py`<br>`.gitignore` | ✅ **PASS**<br>• Match ID consistency, job status transitions (`uploaded` -> `queued`/`processing` -> `completed` / `failed`).<br>• Saved result retrieval from disk without re-inference.<br>• Secure media streaming (`/media/{id}/video`, `/media/{id}/annotated.mp4`).<br>• Local offline backup assets in `backend/data/results/backup_demo/`. |

---

## 🎯 Hours 10–11 Final Release Checklist

- [x] **1. Upload -> analyze -> report works end-to-end**: Smooth transition with real-time status polling.
- [x] **2. At least 3 displayed metrics are real and have units**: `distance_m`, `court_coverage`, `rear_court_dist` (or `tracked_samples`, `active_players` if uncalibrated).
- [x] **3. Court heatmap is based on valid mapped positions**: Normalized BWF court [0..1] with position filtering.
- [x] **4. An evidence event replays the correct original-video moment**: Click-to-seek updates video player directly to timestamp.
- [x] **5. No fabricated score, confidence or accuracy claim**: Truthful calculations; uncalibrated metrics show "Not available" + reason.
- [x] **6. Fresh startup instructions and backup report are ready**: Tested scripts `run_backend.bat` and `run_frontend.bat`; backup fixture at `backend/data/results/backup_demo/`.
- [x] **7. All changes committed; main branch is runnable**: Verified and ready for judges.

---

## 🎤 5-Minute Presentation Demo Script (Hours 10–11)

| Time | Show | Say |
| :--- | :--- | :--- |
| **0:00 - 0:35** | **Problem** | *"Smaller clubs, academies, and amateur players often lack affordable, structured video analysis. Expensive multi-camera tracking systems are out of reach."* |
| **0:35 - 1:15** | **Upload + Calibration** | *"Here is ordinary recorded badminton footage. By marking the four court corners, RallyLens establishes a perspective homography matrix to normalize the camera view into metric space."* |
| **1:15 - 2:10** | **Real Tracking** | *"Notice the player tracks and court-zone heatmap. Everything is calculated frame-by-frame on CPU using YOLOv8 person detection and multi-frame tracking."* |
| **2:10 - 3:20** | **Evidence-Linked Insight** | *"Watch as we click this movement event. The video seeks directly to the exact rally moment. We see the measured repositioning pattern and a cautious coaching recommendation."* |
| **3:20 - 4:15** | **Architecture** | *"Our architecture decouples sport rules and dimensions in a modular configuration schema, allowing homography re-use across court sports."* |
| **4:15 - 5:00** | **Impact + Limitations** | *"RallyLens democratizes tactical feedback from a single camera. We honestly report tracking limitations under severe occlusions and require calibration for physical distances."* |

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
*(Web Application: `http://localhost:5173`)*

---

## 🧪 Automated Verification Suite
Run the full Hours 10–11 sprint test suite:
```powershell
cd backend
.\.venv\Scripts\python.exe test_hour_10_11_sprint.py
```
