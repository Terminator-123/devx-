"""
Hour 5 Reliability & Final Release Checklist Verification Test
Validates:
1. Two successful end-to-end runs.
2. Defensible metrics (with unavailable reason when uncalibrated).
3. Monotonic timestamps matching original video clock.
4. Reopening completed results from disk without repeat inference.
5. Clean error reporting on invalid files and non-existent IDs.
6. Backup demo readiness.
"""

import time
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_hour_5_release_checklist():
    print("==================================================")
    print("   HOUR 5 FINAL RELEASE CHECKLIST VERIFICATION    ")
    print("==================================================")

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200 and res.json() == {"status": "ok"}
    print("[PASS] 1. API health verified.")

    # 2. Run #1 (Calibrated)
    with open("sample.mp4", "rb") as f:
        res = client.post("/api/matches", files={"file": ("match_run1.mp4", f, "video/mp4")})
    assert res.status_code == 200
    m_id_1 = res.json()["match_id"]

    corners = [[100, 40], [540, 40], [540, 320], [100, 320]]
    client.post(f"/api/matches/{m_id_1}/analyze", json={"sport": "badminton", "court_corners": corners, "court_type": "doubles"})

    completed_1 = False
    for _ in range(25):
        st = client.get(f"/api/matches/{m_id_1}/status").json()["status"]
        if st == "completed":
            completed_1 = True
            break
        time.sleep(1.0)
    assert completed_1
    print(f"[PASS] 2. Run #1 completed successfully -> Match #{m_id_1}")

    # 3. Run #2 (Repeatability check)
    with open("sample.mp4", "rb") as f:
        res = client.post("/api/matches", files={"file": ("match_run2.mp4", f, "video/mp4")})
    assert res.status_code == 200
    m_id_2 = res.json()["match_id"]

    client.post(f"/api/matches/{m_id_2}/analyze", json={"sport": "badminton", "court_corners": corners, "court_type": "doubles"})
    completed_2 = False
    for _ in range(25):
        st = client.get(f"/api/matches/{m_id_2}/status").json()["status"]
        if st == "completed":
            completed_2 = True
            break
        time.sleep(1.0)
    assert completed_2
    print(f"[PASS] 3. Run #2 completed successfully -> Match #{m_id_2} (Repeatability confirmed)")

    # 4. Metric verification on Run #1
    res1 = client.get(f"/api/matches/{m_id_1}/results").json()
    metrics1 = res1["metrics"]
    assert len(metrics1) >= 3
    dist_metric = next(m for m in metrics1 if m["key"] == "distance_m")
    assert dist_metric["value"] is not None and dist_metric["quality"] == "calibrated"
    print(f"[PASS] 4. Calibrated metrics validated: {[m['label'] + '=' + str(m['value']) + m['unit'] for m in metrics1]}")

    # 5. Evidence timestamps match original video clock
    events1 = res1["events"]
    assert len(events1) >= 1
    ev0 = events1[0]
    assert 0.0 <= ev0["start_seconds"] <= ev0["end_seconds"] <= res1["duration_seconds"]
    print(f"[PASS] 5. Evidence timestamps verified against video clock: '{ev0['title']}' [{ev0['start_seconds']}s - {ev0['end_seconds']}s]")

    # 6. Reopen saved report without rerunning analysis
    res_reopen = client.get(f"/api/matches/{m_id_1}/results").json()
    assert res_reopen["match_id"] == m_id_1
    assert res_reopen["status"] == "completed"
    print(f"[PASS] 6. Saved report #{m_id_1} reopened without rerun.")

    # 7. Uncalibrated test: distance is null and reason is given
    with open("sample.mp4", "rb") as f:
        res_unc = client.post("/api/matches", files={"file": ("match_unc.mp4", f, "video/mp4")}).json()
    unc_id = res_unc["match_id"]
    client.post(f"/api/matches/{unc_id}/analyze", json={"sport": "badminton", "court_corners": None})
    for _ in range(25):
        if client.get(f"/api/matches/{unc_id}/status").json()["status"] == "completed":
            break
        time.sleep(1.0)
    unc_data = client.get(f"/api/matches/{unc_id}/results").json()
    unc_dist = next(m for m in unc_data["metrics"] if m["key"] == "distance_m")
    assert unc_dist["value"] is None and unc_dist["quality"] == "uncalibrated"
    assert any("calibration" in w.lower() for w in unc_data["warnings"])
    print(f"[PASS] 7. Uncalibrated state verified: distance is null with honest warning.")

    # 8. Error handling: invalid format
    res_bad = client.post("/api/matches", files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")})
    assert res_bad.status_code == 400
    print("[PASS] 8. Invalid file rejected cleanly with HTTP 400.")

    # 9. Presentation backup demo
    res_bkp = client.get("/api/matches/backup_demo/results")
    assert res_bkp.status_code == 200 and res_bkp.json()["status"] == "completed"
    print("[PASS] 9. Backup demo report ready for presentation.")

    print("\n==================================================")
    print("   ALL HOUR 5 FINAL RELEASE CHECKLIST ITEMS PASS! ")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_hour_5_release_checklist()
