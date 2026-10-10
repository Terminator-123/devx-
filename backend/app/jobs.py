"""
In-memory job management and pipeline integration.
Member 4: Backend API Lead (Hour 3)
"""

import os
import json
import uuid
import threading
import logging
from typing import Dict, Any, Optional

from .vision.video import process_match

logger = logging.getLogger(__name__)

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# In-memory job state dictionary
JOBS: Dict[str, Dict[str, Any]] = {}


def create_match_job(file_path: str, filename: str) -> str:
    match_id = str(uuid.uuid4())[:8]
    JOBS[match_id] = {
        "match_id": match_id,
        "status": "uploaded",
        "file_path": file_path,
        "filename": filename,
        "sport": "badminton",
        "court_type": "doubles",
        "court_corners": None,
        "output_dir": os.path.join(RESULTS_DIR, match_id),
        "results": None,
        "error": None
    }
    return match_id


def get_job(match_id: str) -> Optional[Dict[str, Any]]:
    # If in memory, return it
    if match_id in JOBS:
        return JOBS[match_id]

    # Reopen from disk if saved report exists (Hour 4 acceptance requirement)
    match_out_dir = os.path.join(RESULTS_DIR, match_id)
    tracking_path = os.path.join(match_out_dir, "tracking.json")
    if os.path.exists(tracking_path):
        try:
            with open(tracking_path, "r", encoding="utf-8") as f:
                saved_results = json.load(f)

            # Locate uploaded file if still present
            uploaded_file = None
            if os.path.exists(UPLOADS_DIR):
                for f_name in os.listdir(UPLOADS_DIR):
                    if match_id in f_name:
                        uploaded_file = os.path.join(UPLOADS_DIR, f_name)
                        break

            JOBS[match_id] = {
                "match_id": match_id,
                "status": "completed",
                "file_path": uploaded_file or "",
                "filename": os.path.basename(uploaded_file) if uploaded_file else f"{match_id}.mp4",
                "sport": saved_results.get("sport", "badminton"),
                "court_type": "doubles",
                "court_corners": None,
                "output_dir": match_out_dir,
                "results": saved_results,
                "error": None
            }
            return JOBS[match_id]
        except Exception as e:
            logger.warning(f"Failed to restore saved report {match_id} from disk: {e}")

    return None


def start_analysis_task(
    match_id: str,
    sport: str = "badminton",
    court_corners: Optional[list] = None,
    court_type: str = "doubles"
):
    job = get_job(match_id)
    if not job:
        raise KeyError(f"Match '{match_id}' not found")

    # If already completed with results on disk, do not rerun unnecessarily
    if job.get("status") == "completed" and job.get("results"):
        return

    job["status"] = "processing"
    job["sport"] = sport
    job["court_type"] = court_type
    job["court_corners"] = court_corners

    output_dir = job["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    thread = threading.Thread(
        target=_run_pipeline_worker,
        args=(match_id, job["file_path"], output_dir, court_corners, court_type, sport),
        daemon=True
    )
    thread.start()


def _run_pipeline_worker(
    match_id: str,
    video_path: str,
    output_dir: str,
    court_corners: Optional[list],
    court_type: str,
    sport: str
):
    job = JOBS.get(match_id)
    if not job:
        return

    try:
        # Call Member 1's stable process_match pipeline function
        raw_result = process_match(
            video_path=video_path,
            sport=sport,
            court_corners=court_corners,
            court_type=court_type,
            output_dir=output_dir
        )

        media_urls = {
            "original_video": f"/media/{match_id}/video",
            "annotated_video": f"/media/{match_id}/annotated.mp4" if raw_result.get("annotated_video") else None,
            "annotated_preview": f"/media/{match_id}/annotated_preview.jpg" if raw_result.get("annotated_frame") else None
        }

        # Attach evidence URL if available
        for evt in raw_result.get("events", []):
            evt["evidence_url"] = f"/media/{match_id}/annotated.mp4"

        normalized_result = {
            "match_id": match_id,
            "sport": sport,
            "status": "completed",
            "duration_seconds": raw_result.get("duration_seconds", 0.0),
            "metrics": raw_result.get("metrics", []),
            "events": raw_result.get("events", []),
            "tracks": raw_result.get("tracks", []),
            "heatmap": raw_result.get("heatmap", {"width": 10, "height": 5, "cells": []}),
            "warnings": raw_result.get("warnings", []),
            "media_urls": media_urls
        }

        job["results"] = normalized_result
        job["status"] = "completed"

        # Persist final JSON
        result_json_path = os.path.join(output_dir, "tracking.json")
        with open(result_json_path, "w", encoding="utf-8") as f:
            json.dump(normalized_result, f, indent=2)

    except Exception as exc:
        logger.exception(f"Pipeline error on match {match_id}: {exc}")
        # Hour 3 Rule: Do NOT fall back to fabricated mock metrics. Mark failed.
        job["status"] = "failed"
        job["error"] = str(exc)
