"""
Deterministic vision pipeline for badminton recordings.
Member 1: AI Lead (Hour 3)

Contract:
process_match(video_path, sport="badminton", court_corners=None, court_type="doubles") -> result_dict
"""

import os
import json
from typing import List, Dict, Any, Optional
import cv2
import numpy as np

from .calibration import CourtCalibrator
from .tracking import MultiFramePlayerTracker
from .metrics import compute_validated_metrics
from .evidence import extract_evidence_events

_YOLO_MODEL = None


def get_yolo_model():
    global _YOLO_MODEL
    if _YOLO_MODEL is None:
        from ultralytics import YOLO
        _YOLO_MODEL = YOLO("yolov8n.pt")
    return _YOLO_MODEL


def process_single_frame(frame: np.ndarray, model=None, conf: float = 0.25) -> List[Dict[str, Any]]:
    if model is None:
        model = get_yolo_model()
    results = model.predict(frame, imgsz=640, conf=conf, verbose=False)
    detections = []
    for r in results:
        for box in r.boxes:
            if int(box.cls[0].item()) == 0:
                xyxy = box.xyxy[0].tolist()
                detections.append({
                    "bbox": xyxy,
                    "confidence": float(box.conf[0].item()),
                    "track_id": None
                })
    return detections


def process_match(
    video_path: str,
    sport: str = "badminton",
    court_corners: Optional[List[List[float]]] = None,
    court_type: str = "doubles",
    output_dir: Optional[str] = None,
    max_seconds: float = 60.0
) -> Dict[str, Any]:
    """
    Member 1 stable pipeline contract:
    process_match(video_path, sport, court_corners, court_type) -> result_dict
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    if output_dir is None:
        output_dir = os.path.dirname(video_path)

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot read video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_seconds = round(total_frames / max(fps, 1.0), 2)

    calibrator = CourtCalibrator(
        court_corners=court_corners,
        frame_size=(width, height),
        court_type=court_type
    )
    tracker = MultiFramePlayerTracker()
    model = get_yolo_model()

    warnings = []
    if not calibrator.is_valid:
        warnings.append("Court calibration invalid or not provided: court_x/court_y and metre metrics omitted.")

    # Setup annotated video output
    annotated_video_path = os.path.join(output_dir, "annotated.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(annotated_video_path, fourcc, min(fps, 25.0), (width, height))

    sample_interval = max(1, int(fps / 2))
    player_tracks: Dict[int, List[Dict[str, Any]]] = {1: [], 2: []}
    first_annotated_frame = None

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_seconds = round(frame_idx / fps, 2)
        if timestamp_seconds > max_seconds:
            warnings.append(f"Analysis capped at {max_seconds}s for CPU efficiency.")
            break

        if frame_idx % sample_interval == 0:
            results = model.predict(frame, imgsz=640, conf=0.25, verbose=False)
            raw_detections = []
            for r in results:
                for box in r.boxes:
                    if int(box.cls[0].item()) == 0:  # person
                        xyxy = box.xyxy[0].tolist()
                        conf = float(box.conf[0].item())
                        raw_detections.append({
                            "bbox": xyxy,
                            "confidence": conf,
                            "track_id": None
                        })

            matched = tracker.update(raw_detections, frame_width=width, frame_height=height)

            annotated_frame = frame.copy()
            for m in matched:
                pid = m["player_id"]
                foot_x = m["foot_x"]
                foot_y = m["foot_y"]

                court_pt = calibrator.map_point(foot_x, foot_y) if calibrator.is_valid else None
                calib_valid = bool(court_pt is not None)

                # Normalized sample matching Hour 3 schema
                sample = {
                    "timestamp_seconds": timestamp_seconds,
                    "player_id": pid,
                    "bbox_xyxy": m["bbox"],
                    "footpoint_px": [foot_x, foot_y],
                    "detector_confidence": m["confidence"],
                    "court_x": round(court_pt[0], 3) if court_pt else None,
                    "court_y": round(court_pt[1], 3) if court_pt else None,
                    "calibration_valid": calib_valid
                }

                if pid not in player_tracks:
                    player_tracks[pid] = []
                player_tracks[pid].append(sample)

                # Render annotations
                x1, y1, x2, y2 = [int(v) for v in m["bbox"]]
                col = (0, 220, 100) if pid == 1 else (255, 140, 20)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), col, 2)
                cv2.circle(annotated_frame, (int(foot_x), int(foot_y)), 5, (0, 0, 255), -1)
                cv2.putText(
                    annotated_frame,
                    f"P{pid} ({m['confidence']:.2f})",
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    col,
                    2
                )

            if first_annotated_frame is None and matched:
                first_annotated_frame = annotated_frame.copy()

            out_writer.write(annotated_frame)

        frame_idx += 1

    cap.release()
    out_writer.release()

    # Save preview image
    annotated_frame_file = "annotated_preview.jpg"
    if first_annotated_frame is not None:
        cv2.imwrite(os.path.join(output_dir, annotated_frame_file), first_annotated_frame)
    else:
        annotated_frame_file = None

    # Construct sorted tracks
    tracks_result = []
    for pid in sorted(player_tracks.keys()):
        samples = player_tracks[pid]
        # Sort samples by timestamp
        samples.sort(key=lambda s: s["timestamp_seconds"])
        if samples:
            tracks_result.append({
                "player_id": pid,
                "samples": samples
            })

    # Compute metrics & heatmap
    metrics_list, heatmap_obj, metric_warns = compute_validated_metrics(
        tracks=tracks_result,
        duration_seconds=duration_seconds,
        court_calibrated=calibrator.is_valid,
        court_width_m=calibrator.court_width_m,
        court_length_m=calibrator.court_length_m
    )
    warnings.extend(metric_warns)

    # Compute evidence events
    events_list = extract_evidence_events(
        tracks=tracks_result,
        duration_seconds=duration_seconds,
        court_calibrated=calibrator.is_valid
    )

    result_payload = {
        "duration_seconds": duration_seconds,
        "tracks": tracks_result,
        "metrics": metrics_list,
        "heatmap": heatmap_obj,
        "events": events_list,
        "warnings": warnings,
        "annotated_video": "annotated.mp4",
        "annotated_frame": annotated_frame_file
    }

    # Save tracking.json
    tracking_json_path = os.path.join(output_dir, "tracking.json")
    with open(tracking_json_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)

    return result_payload


# Flexible wrapper for analyze_video matching Hour 6 and Hour 1-5 signatures
def analyze_video(
    video_path: str,
    output_dir: Optional[str] = None,
    court_corners: Optional[list] = None,
    court_type: str = "doubles",
    sport: str = "badminton",
    sport_config: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    # If output_dir was passed as sport_config dict/string or None
    out = output_dir
    if isinstance(out, (dict, str)) and ("/" not in str(out) and "\\" not in str(out) and not os.path.isdir(str(out))):
        # Likely sport name or config
        sport = str(out)
        out = kwargs.get("output_dir", os.path.dirname(video_path))

    return process_match(
        video_path=video_path,
        sport=sport,
        court_corners=court_corners,
        court_type=court_type,
        output_dir=out or os.path.dirname(video_path)
    )
