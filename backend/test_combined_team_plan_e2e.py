"""
Combined Team Plan (Hours 6-8 + Buffer) End-to-End Verification Test
Verifies all 9 items on the Final Release Checklist (Page 5).
"""

import time
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_final_release_checklist():
    print("==================================================")
    print(" COMBINED TEAM PLAN (HOURS 6-8) RELEASE CHECKLIST ")
    print("==================================================")

    # 1. Health check (Backend start)
    res = client.get("/api/health")
    assert res.status_code == 200 and res.json() == {"status": "ok"}
    print("[PASS] Check 1: Backend service running and healthy.")

    # 2. Complete analysis twice (Repeatability check)
    match_ids = []
    for run_idx in (1, 2):
        with open("sample.mp4", "rb") as f:
            res_up = client.post("/api/matches", files={"file": (f"clip_run_{run_idx}.mp4", f, "video/mp4")})
        assert res_up.status_code == 200
        mid = res_up.json()["match_id"]
        match_ids.append(mid)

        corners = [[100, 40], [540, 40], [540, 320], [100, 320]]
        res_an = client.post(
            f"/api/matches/{mid}/analyze",
            json={"sport": "badminton", "court_type": "doubles", "court_corners": corners}
        )
        assert res_an.status_code == 200

        # Poll until complete
        done = False
        for _ in range(25):
            st = client.get(f"/api/matches/{mid}/status").json()["status"]
            if st == "completed":
                done = True
                break
            time.sleep(1.0)
        assert done, f"Run {run_idx} failed to complete"
        print(f"       Run #{run_idx} completed successfully (Match #{mid}).")

    print("[PASS] Check 2: One recorded clip completed analysis twice consecutively.")

    # 3. Three displayed metrics use real calculated values
    res_final = client.get(f"/api/matches/{match_ids[0]}/results").json()
    metrics = res_final.get("metrics", [])
    assert len(metrics) >= 3, f"Expected at least 3 metrics, found {len(metrics)}"
    for m in metrics:
        assert m["value"] is not None, f"Expected calculated value for metric {m['key']}"
        assert m["quality"] == "calibrated"
    print(f"[PASS] Check 3: Three displayed metrics use real calculated values: {[m['label'] + '=' + str(m['value']) + m['unit'] for m in metrics]}")

    # 4. Heatmap uses valid court-coordinate positions [0..1]
    tracks = res_final.get("tracks", [])
    assert len(tracks) >= 2, "Expected 2 players tracked"
    for t in tracks:
        for s in t.get("samples", []):
            if s.get("calibration_valid"):
                assert s["court_x"] is not None and 0.0 <= s["court_x"] <= 1.0, f"Invalid court_x: {s['court_x']}"
                assert s["court_y"] is not None and 0.0 <= s["court_y"] <= 1.0, f"Invalid court_y: {s['court_y']}"
    heatmap_cells = res_final.get("heatmap", {}).get("cells", [])
    assert len(heatmap_cells) > 0, "Expected non-empty heatmap cells"
    print(f"[PASS] Check 4: Heatmap and tracks use valid bounded court-coordinates [0..1] ({len(heatmap_cells)} heatmap cells).")

    # 5. At least one evidence event seeks to correct segment
    events = res_final.get("events", [])
    assert len(events) >= 1, "Expected at least 1 evidence event"
    for ev in events:
        assert 0.0 <= ev["start_seconds"] <= ev["end_seconds"] <= res_final["duration_seconds"]
    print(f"[PASS] Check 5: Evidence events validated against video clock: {[e['title'] + ' (' + str(e['start_seconds']) + 's)' for e in events]}")

    # 6. No visible mock values in the real report
    assert "mock" not in res_final.get("status", "").lower()
    for m in metrics:
        assert m.get("quality") != "mock"
    print("[PASS] Check 6: No mock values in real report output.")

    # 7. Error states work for invalid upload or failed analysis
    res_err1 = client.post("/api/matches", files={"file": ("bad.exe", b"binary", "application/octet-stream")})
    assert res_err1.status_code == 400
    res_err2 = client.get("/api/matches/unknown_match_999/results")
    assert res_err2.status_code == 404
    print("[PASS] Check 7: Error states verified for invalid file and unknown ID.")

    # 8. Backup processed clip/report is available offline
    backup_path = os.path.join("data", "results", "backup_demo", "tracking.json")
    assert os.path.exists(backup_path), "Backup tracking.json missing"
    res_bkp = client.get("/api/matches/backup_demo/results")
    assert res_bkp.status_code == 200
    print("[PASS] Check 8: Backup processed report available offline at data/results/backup_demo/.")

    # 9. Media streams play
    res_vid = client.get(f"/media/{match_ids[0]}/video")
    assert res_vid.status_code == 200 and len(res_vid.content) > 0
    res_ann = client.get(f"/media/{match_ids[0]}/annotated.mp4")
    assert res_ann.status_code == 200 and len(res_ann.content) > 0
    print("[PASS] Check 9: Original and annotated media streams playable.")

    print("\n==================================================")
    print("   ALL FINAL RELEASE CHECKLIST ITEMS PASSED!      ")
    print("==================================================")
    return True

if __name__ == "__main__":
    test_final_release_checklist()
