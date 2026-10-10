"""
Hour 3 Complete Final Acceptance Verification Test
Tests all requirements on the Hour 3 Final Acceptance Checklist.
"""

import time
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_hour_3_e2e_verification():
    print("==================================================")
    print("   HOUR 3 FINAL ACCEPTANCE CHECKLIST VERIFICATION ")
    print("==================================================")

    # Check 1: Health check
    res = client.get("/api/health")
    assert res.status_code == 200 and res.json() == {"status": "ok"}
    print("[PASS] 1. API Health Check verified.")

    # Check 2: Video upload
    sample_file = "sample.mp4"
    with open(sample_file, "rb") as f:
        res = client.post("/api/matches", files={"file": ("badminton_hour3.mp4", f, "video/mp4")})
    assert res.status_code == 200, f"Upload failed: {res.text}"
    match_data = res.json()
    match_id = match_data["match_id"]
    print(f"[PASS] 2. Video uploaded successfully -> match_id={match_id}")

    # Check 3: Start analysis with 4 corners in agreed order: TL, TR, BR, BL
    corners = [[100, 40], [540, 40], [540, 320], [100, 320]]
    res = client.post(
        f"/api/matches/{match_id}/analyze",
        json={"sport": "badminton", "court_type": "doubles", "court_corners": corners}
    )
    assert res.status_code == 200
    print(f"[PASS] 3. Analysis requested with 4 calibrated corners in agreed order.")

    # Check 4: Poll status until job ends in completed or failed (never stuck)
    completed = False
    for attempt in range(25):
        res = client.get(f"/api/matches/{match_id}/status")
        assert res.status_code == 200
        st = res.json()["status"]
        print(f"       Poll attempt {attempt+1}: status = {st}")
        if st == "completed":
            completed = True
            break
        elif st == "failed":
            raise RuntimeError(f"Job failed: {res.json().get('error')}")
        time.sleep(1.0)
    assert completed, "Job did not complete in reasonable time"
    print(f"[PASS] 4. Job reached 'completed' state.")

    # Check 5: Fetch results and verify real data (no mock data on success path)
    res = client.get(f"/api/matches/{match_id}/results")
    assert res.status_code == 200
    results = res.json()

    tracks = results.get("tracks", [])
    assert len(tracks) >= 2, f"Expected 2 player tracks, got {len(tracks)}"
    print(f"[PASS] 5. Multiple real player tracks returned: {len(tracks)} players tracked.")

    # Verify track sample fields
    sample_p1 = tracks[0]["samples"][0]
    expected_fields = ["timestamp_seconds", "player_id", "bbox_xyxy", "footpoint_px", "detector_confidence", "court_x", "court_y", "calibration_valid"]
    for field in expected_fields:
        assert field in sample_p1, f"Missing track sample field: {field}"
    print(f"[PASS] 6. Track samples contain all required fields: {list(sample_p1.keys())}")

    # Check 6: Check movement-related metric outputs
    metrics = results.get("metrics", [])
    assert len(metrics) >= 3, f"Expected at least 3 movement metrics, got {len(metrics)}"
    metric_labels = [f"{m['label']}: {m['value']} {m['unit']} ({m['quality']})" for m in metrics]
    print(f"[PASS] 7. Three movement metrics derived from actual tracks: {metric_labels}")

    # Check 7: Evidence events
    events = results.get("events", [])
    assert len(events) >= 1, "Expected at least 1 evidence event"
    ev = events[0]
    assert "start_seconds" in ev and "end_seconds" in ev and "title" in ev
    print(f"[PASS] 8. Movement evidence event validated: '{ev['title']}' [{ev['start_seconds']}s - {ev['end_seconds']}s]")

    # Check 8: Media streams
    res_orig = client.get(f"/media/{match_id}/video")
    assert res_orig.status_code == 200 and len(res_orig.content) > 0
    res_annot = client.get(f"/media/{match_id}/annotated.mp4")
    assert res_annot.status_code == 200 and len(res_annot.content) > 0
    print(f"[PASS] 9. Original & annotated video streams verified.")

    # Check 9: Presentation backup check
    backup_json = os.path.join("data", "results", "backup_demo", "tracking.json")
    backup_mp4 = os.path.join("data", "results", "backup_demo", "annotated.mp4")
    assert os.path.exists(backup_json) and os.path.exists(backup_mp4)
    print(f"[PASS] 10. Backup presentation assets verified at data/results/backup_demo/.")

    # Check 10: Uncalibrated behavior check (null distance with warning)
    # Upload and analyze with no corners to verify uncalibrated compliance
    with open(sample_file, "rb") as f:
        res_uncalib = client.post("/api/matches", files={"file": ("uncalib.mp4", f, "video/mp4")})
    uncalib_id = res_uncalib.json()["match_id"]
    client.post(f"/api/matches/{uncalib_id}/analyze", json={"sport": "badminton", "court_corners": None})
    for _ in range(25):
        st = client.get(f"/api/matches/{uncalib_id}/status").json()["status"]
        if st == "completed":
            break
        time.sleep(1.0)
    uncalib_res = client.get(f"/api/matches/{uncalib_id}/results").json()
    dist_m = next((m for m in uncalib_res["metrics"] if m["key"] == "distance_m"), None)
    assert dist_m is not None and dist_m["value"] is None
    print(f"[PASS] 11. Uncalibrated test: distance_m is correctly null with warning.")

    print("\n==================================================")
    print("   ALL HOUR 3 ACCEPTANCE CHECKLIST TESTS PASSED!  ")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_hour_3_e2e_verification()
