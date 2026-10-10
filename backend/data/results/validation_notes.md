# RallyLens AI — AI Pipeline Validation Notes (Hours 10–11)

## 1. Multi-Frame Tracking Benchmark
- **Test Clip**: `backend/sample.mp4` (Duration: 4.0s, 25 FPS)
- **Model**: `yolov8n.pt` (COCO person class 0, imgsz=640, conf=0.25)
- **Sample Rate**: 2 FPS (every 12 frames on 25 FPS footage)
- **Runtime**: ~1.8 seconds on CPU for 4.0s clip (real-time factor ~0.45x)
- **Tracks Identified**:
  - `Player 1` (Near Court / Baseline): 9 sample observations
  - `Player 2` (Far Court / Net Area): 5-9 sample observations
  - **Timestamps**: Monotonically increasing `[0.0s, 0.48s, 0.96s, ..., 3.84s]`
  - **ID Stability**: Consistent 1 and 2 throughout trajectory; no ID swapping detected.

## 2. Court Mapping & Metre Calculations
- **Corner Order**: `[Top-Left, Top-Right, Bottom-Right, Bottom-Left]`
- **Homography Matrix**: Perspective transform into standard BWF court dimensions:
  - Doubles: 13.4m length × 6.1m width
  - Singles: 13.4m length × 5.18m width
- **Quality Check**:
  - Distance moved: Calculated strictly as step-wise Euclidean distance between consecutive normalized court coordinates mapped to real metres. Out-of-court anomalies and impossible jumps (>4.0m per step) are filtered out.
  - When uncalibrated: Metric distance in metres is set to `null` with warning `"Court calibration not provided: distance in metres is null"`.

## 3. Rally Evidence Loop Verification
- **Event 1**: `evt_move_001` (0.0s → 1.4s): Baseline lateral movement and positioning.
  - Suggestion: *"Maintain balanced split-step at baseline to reduce reaction latency on fast drives."*
- **Event 2**: `evt_move_002` (1.44s → 2.8s): Mid-court attack and rapid recovery.
  - Suggestion: *"Recover immediately to court center (T-junction) following front-court interception."*
- **Event 3**: `evt_move_003` (2.88s → 3.84s): Rear-court movement and court repositioning.
  - Suggestion: *"Prioritize scissor kick or deep recovery step to prevent getting trapped behind baseline."*
- **Traceability**: Each insight links directly from a measured tracking delta to a video clip seek point and a cautious tactical suggestion.

## 4. 20-Second AI Limitations Statement (For Judge Walkthrough)
> *"RallyLens operates on a single stationary camera without specialized sensor hardware. As a result, tracking accuracy depends on clear line-of-sight: severe player occlusion or players exiting camera frame will degrade footpoint estimation. Furthermore, real metric distances strictly require manual 4-corner court calibration; when footage is uncalibrated, our engine honestly omits metre calculations rather than hallucinating distance figures. Finally, tactical insights represent physical movement observations, not automatic line-calling or shuttlecock trajectories."*

## 5. Output Artifacts
- **Primary JSON**: `backend/data/results/<match_id>/tracking.json`
- **Annotated Video**: `backend/data/results/<match_id>/annotated.mp4`
- **Preview Frame**: `backend/data/results/<match_id>/annotated_preview.jpg`
- **Presentation Backup**: `backend/data/results/backup_demo/`
