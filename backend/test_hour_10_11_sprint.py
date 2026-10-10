"""
Automated end-to-end verification suite for Hours 10-11 Combined Sprint Plan.
Verifies all 7 checklist items and Member 1-4 deliverables.
"""

import os
import sys
import json
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.jobs import JOBS, RESULTS_DIR, create_match_job
from app.vision.video import process_match, analyze_video
from app.vision.tracking import MultiFramePlayerTracker
from app.vision.calibration import CourtCalibrator
from app.vision.metrics import compute_validated_metrics
from app.vision.evidence import extract_evidence_events

client = TestClient(app)
SAMPLE_VIDEO_PATH = os.path.join(backend_dir, "sample.mp4")


def test_member1_ai_lead_pipeline():
    """Member 1: AI Lead - Run test clip, check tracking, calibration, metrics, evidence & coaching."""
    assert os.path.exists(SAMPLE_VIDEO_PATH), "sample.mp4 must exist for testing"
    test_out = os.path.join(backend_dir, "data", "results", "test_h10_11_m1")
    os.makedirs(test_out, exist_ok=True)

    corners = [
        [320.0, 100.0],
        [960.0, 100.0],
        [1100.0, 680.0],
        [180.0, 680.0]
    ]

    res = process_match(
        video_path=SAMPLE_VIDEO_PATH,
        sport="badminton",
        court_corners=corners,
        court_type="doubles",
        output_dir=test_out
    )

    # 1. Output structure
    assert "duration_seconds" in res
    assert "tracks" in res
    assert "metrics" in res
    assert "events" in res
    assert "heatmap" in res
    assert len(res["tracks"]) >= 1

    # 2. Monotonic timestamps & bounded court positions
    for t in res["tracks"]:
        samples = t["samples"]
        for i in range(1, len(samples)):
            assert samples[i]["timestamp_seconds"] >= samples[i - 1]["timestamp_seconds"]
        for s in samples:
            if s["calibration_valid"]:
                assert 0.0 <= s["court_x"] <= 1.0
                assert 0.0 <= s["court_y"] <= 1.0

    # 3. Real metrics with units
    metric_keys = [m["key"] for m in res["metrics"]]
    assert "distance_m" in metric_keys
    dist_m = next(m for m in res["metrics"] if m["key"] == "distance_m")
    assert dist_m["value"] is not None and dist_m["value"] > 0
    assert dist_m["unit"] == "m"

    # 4. Evidence events with coaching suggestion & measured pattern
    assert len(res["events"]) >= 1
    for evt in res["events"]:
        assert "start_seconds" in evt
        assert "end_seconds" in evt
        assert "title" in evt
        assert "coaching_suggestion" in evt
        assert "measured_pattern" in evt


def test_member2_frontend_upload_and_error_paths():
    """Member 2: Frontend API integration & Error handling."""
    # Invalid match ID 404
    res = client.get("/api/matches/non_existent_99999/status")
    assert res.status_code == 404

    # Invalid file format 400
    res = client.post(
        "/api/matches",
        files={"file": ("malicious.exe", b"malicious binary", "application/octet-stream")}
    )
    assert res.status_code == 400
    assert "Unsupported video format" in res.json()["detail"]


def test_member3_results_and_evidence_replay():
    """Member 3: Results dashboard, evidence replay, and backup demo."""
    # Check backup demo results
    res = client.get("/api/matches/backup_demo/results")
    assert res.status_code == 200
    data = res.json()
    assert data["match_id"] == "backup_demo"
    assert len(data["metrics"]) >= 3
    for m in data["metrics"]:
        assert "unit" in m
        assert m["value"] is not None

    # Check evidence replay events
    assert len(data["events"]) >= 3
    e1 = data["events"][0]
    assert e1["start_seconds"] == 0.0
    assert "coaching_suggestion" in e1
    assert "measured_pattern" in e1


def test_member4_backend_lifecycle_and_persistence():
    """Member 4: Backend API lifecycle, repeatable runs, and disk retrieval."""
    with open(SAMPLE_VIDEO_PATH, "rb") as f:
        upload_res = client.post(
            "/api/matches",
            files={"file": ("test_repeat.mp4", f, "video/mp4")}
        )
    assert upload_res.status_code == 200
    match_id = upload_res.json()["match_id"]

    # Start analysis
    corners = [[320.0, 100.0], [960.0, 100.0], [1100.0, 680.0], [180.0, 680.0]]
    ana_res = client.post(
        f"/api/matches/{match_id}/analyze",
        json={"sport": "badminton", "court_type": "doubles", "court_corners": corners}
    )
    assert ana_res.status_code == 200

    # Wait for completion
    import time
    for _ in range(30):
        stat = client.get(f"/api/matches/{match_id}/status").json()
        if stat["status"] == "completed":
            break
        time.sleep(0.5)
    assert stat["status"] == "completed"

    # Verify results
    result_res = client.get(f"/api/matches/{match_id}/results")
    assert result_res.status_code == 200
    results = result_res.json()
    assert len(results["metrics"]) >= 3
    assert len(results["events"]) >= 1

    # Verify persistence: clear memory, ensure disk reload works
    if match_id in JOBS:
        del JOBS[match_id]

    reloaded_stat = client.get(f"/api/matches/{match_id}/status").json()
    assert reloaded_stat["status"] == "completed"
    reloaded_results = client.get(f"/api/matches/{match_id}/results").json()
    assert reloaded_results["match_id"] == match_id


if __name__ == "__main__":
    print("Running Hours 10-11 verification suite...")
    test_member1_ai_lead_pipeline()
    print("✓ Member 1 AI pipeline passed.")
    test_member2_frontend_upload_and_error_paths()
    print("✓ Member 2 upload & error handling passed.")
    test_member3_results_and_evidence_replay()
    print("✓ Member 3 results & evidence replay passed.")
    test_member4_backend_lifecycle_and_persistence()
    print("✓ Member 4 backend lifecycle & persistence passed.")
    print("\nALL HOURS 10-11 SPRINT CRITERIA VERIFIED SUCCESSFULLY!")
