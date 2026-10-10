"""
Multi-frame player tracker with persistent IDs and ByteTrack compatibility.
Member 1: AI Lead (Hour 2)
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class MultiFramePlayerTracker:
    """
    Maintains persistent player IDs across sampled video frames.
    Filters detections to person class and tracks player positions with foot-point estimation.
    """
    def __init__(self, max_missing_frames: int = 10, distance_threshold_ratio: float = 0.25):
        self.next_player_id = 1
        # tracks: {player_id: {"centroid": (cx, cy), "last_bbox": [x1,y1,x2,y2], "missing": int, "switches": int}}
        self.active_tracks: Dict[int, Dict[str, Any]] = {}
        self.max_missing = max_missing_frames
        self.dist_thresh_ratio = distance_threshold_ratio
        self.id_switches_detected = 0

    def update(
        self,
        raw_detections: List[Dict[str, Any]],
        frame_width: int,
        frame_height: int
    ) -> List[Dict[str, Any]]:
        """
        raw_detections: list of {"bbox": [x1, y1, x2, y2], "confidence": float, "class": 0, "track_id": Optional[int]}
        Returns list of matched player detections for the current frame:
        [{"player_id": int, "bbox": [x1,y1,x2,y2], "foot_x": float, "foot_y": float, "confidence": float}]
        """
        frame_detections = []
        for det in raw_detections:
            x1, y1, x2, y2 = det["bbox"]
            foot_x = round((x1 + x2) / 2.0, 1)
            foot_y = round(float(y2), 1)
            conf = round(float(det.get("confidence", 0.85)), 3)
            ext_tid = det.get("track_id")
            frame_detections.append({
                "bbox": [round(float(v), 1) for v in [x1, y1, x2, y2]],
                "foot_x": foot_x,
                "foot_y": foot_y,
                "confidence": conf,
                "ext_tid": ext_tid
            })

        if not frame_detections:
            # Increment missing counters
            for tid in list(self.active_tracks.keys()):
                self.active_tracks[tid]["missing"] += 1
                if self.active_tracks[tid]["missing"] > self.max_missing:
                    del self.active_tracks[tid]
            return []

        # If Ultralytics provided persistent track_id (e.g. via model.track), map them
        has_ultralytics_ids = any(d["ext_tid"] is not None for d in frame_detections)
        if has_ultralytics_ids:
            return self._update_with_ext_ids(frame_detections)

        return self._update_with_centroid_distance(frame_detections, frame_height)

    def _update_with_ext_ids(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for det in detections:
            ext_id = det["ext_tid"]
            if ext_id is None:
                continue

            # Map external track ID to stable 1-indexed player ID (1 or 2)
            if ext_id not in self.active_tracks:
                if 1 in self.active_tracks and det["foot_y"] > self.active_tracks[1]["foot_y"]:
                    assigned_pid = 1
                else:
                    assigned_pid = 2
                self.active_tracks[ext_id] = {
                    "player_id": assigned_pid,
                    "foot_x": det["foot_x"],
                    "foot_y": det["foot_y"],
                    "missing": 0
                }
            else:
                self.active_tracks[ext_id]["foot_x"] = det["foot_x"]
                self.active_tracks[ext_id]["foot_y"] = det["foot_y"]
                self.active_tracks[ext_id]["missing"] = 0

            pid = self.active_tracks[ext_id]["player_id"]
            results.append({
                "player_id": pid,
                "bbox": det["bbox"],
                "foot_x": det["foot_x"],
                "foot_y": det["foot_y"],
                "confidence": det["confidence"]
            })
        return results

    def _update_with_centroid_distance(
        self,
        detections: List[Dict[str, Any]],
        frame_height: int
    ) -> List[Dict[str, Any]]:
        # Spatial sorting: top (far player) vs bottom (near player)
        detections.sort(key=lambda d: d["foot_y"])
        results = []

        if not self.active_tracks:
            for idx, det in enumerate(detections[:2]):
                pid = idx + 1
                self.active_tracks[pid] = {
                    "player_id": pid,
                    "foot_x": det["foot_x"],
                    "foot_y": det["foot_y"],
                    "missing": 0
                }
                results.append({
                    "player_id": pid,
                    "bbox": det["bbox"],
                    "foot_x": det["foot_x"],
                    "foot_y": det["foot_y"],
                    "confidence": det["confidence"]
                })
            return results

        dist_thresh = frame_height * self.dist_thresh_ratio
        assigned_det_indices = set()

        for pid in list(self.active_tracks.keys()):
            track = self.active_tracks[pid]
            best_dist = float("inf")
            best_idx = -1

            for idx, det in enumerate(detections):
                if idx in assigned_det_indices:
                    continue
                d = np.hypot(det["foot_x"] - track["foot_x"], det["foot_y"] - track["foot_y"])
                if d < best_dist and d < dist_thresh:
                    best_dist = d
                    best_idx = idx

            if best_idx != -1:
                assigned_det_indices.add(best_idx)
                det = detections[best_idx]
                track["foot_x"] = det["foot_x"]
                track["foot_y"] = det["foot_y"]
                track["missing"] = 0
                results.append({
                    "player_id": pid,
                    "bbox": det["bbox"],
                    "foot_x": det["foot_x"],
                    "foot_y": det["foot_y"],
                    "confidence": det["confidence"]
                })
            else:
                track["missing"] += 1
                if track["missing"] > self.max_missing:
                    del self.active_tracks[pid]

        # Add unassigned if we have fewer than 2 active players
        for idx, det in enumerate(detections):
            if idx not in assigned_det_indices and len(self.active_tracks) < 2:
                new_pid = 1 if 1 not in self.active_tracks else 2
                self.active_tracks[new_pid] = {
                    "player_id": new_pid,
                    "foot_x": det["foot_x"],
                    "foot_y": det["foot_y"],
                    "missing": 0
                }
                results.append({
                    "player_id": new_pid,
                    "bbox": det["bbox"],
                    "foot_x": det["foot_x"],
                    "foot_y": det["foot_y"],
                    "confidence": det["confidence"]
                })

        return results
