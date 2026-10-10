"""
Hour 4 Integration & Demo Readiness Verification Test
Verifies:
1. Two consecutive full end-to-end runs (Repeatability Rule).
2. Reopening a previously completed report without re-analyzing.
3. Bad input rejection (invalid file extension, non-existent match ID).
4. Monotonic timestamps per player track.
5. Presentation backup verification.
"""

import time
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_repeatable_cycle(cycle_num: int):
    print(f"\n--- Running Full Cycle #{cycle_num} ---")
    # 1. Health
    res = client.get("/api/health")
    assert res.status_code == 200

    # 2. Upload
    with open("sample.mp4", "rb") as f:
        res = client.post("/api/matches", files={"file": (f"demo_run_{cycle_num}.mp4", f, "video/mp4")})
    assert res.status_code == 200
    match_id = res.json()["match_id"]
    print(f"Cycle #{cycle_num} [PASS]: Uploaded -> match_id={match_id}")

    # 3. Analyze with 4 calibrated corners
    corners = [[100, 40], [540, 40], [540, 320], [100, 320]]
    res = client.post(
        f"/api/matches/{match_id}/analyze",
        json={"sport": "badminton", "court_type": "doubles", "court_corners": corners}
    )
    assert res.status_code == 200
    print(f"Cycle #{cycle_num} [PASS]: Analysis queued.")

    # 4. Status poll
    completed = False
    for _ in range(25):
        res = client.get(f"/api/matches/{match_id}/status")
        if res.json()["status"] == "completed":
            completed = True
            break
        time.sleep(1.0)
    assert completed, f"Cycle #{cycle_num} failed to complete in time"
    print(f"Cycle #{cycle_num} [PASS]: Status reached 'completed'.")

    # 5. Results
    res = client.get(f"/api/matches/{match_id}/results")
    assert res.status_code == 200
    results = res.json()
    assert len(results["tracks"]) >= 2
    assert len(results["metrics"]) >= 3
    print(f"Cycle #{cycle_num} [PASS]: Results validated with {len(results['tracks'])} tracks and {len(results['metrics'])} metrics.")

    # Verify monotonic timestamps per track
    for t in results["tracks"]:
        timestamps = [s["timestamp_seconds"] for s in t["samples"]]
        assert all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1)), f"Non-monotonic timestamps found in track {t['player_id']}"
    print(f"Cycle #{cycle_num} [PASS]: Monotonic timestamps verified for all tracks.")

    return match_id


def run_hour_4_tests():
    print("==================================================")
    print("     HOUR 4 DEMO READINESS & HARDENING TEST       ")
    print("==================================================")

    # 1. First full run
    match_id_1 = run_repeatable_cycle(1)

    # 2. Second full run (Verifying GO/NO-GO Repeatability Rule)
    match_id_2 = run_repeatable_cycle(2)
    print("\n[GO/NO-GO SUCCESS]: Core flow repeated twice with 100% reliability!")

    # 3. Reopen saved report without rerunning analysis
    print("\n--- Testing Reopen Saved Report ---")
    res_reopen = client.get(f"/api/matches/{match_id_1}/results")
    assert res_reopen.status_code == 200
    assert res_reopen.json()["status"] == "completed"
    print(f"[PASS]: Reopened report #{match_id_1} without re-running analysis.")

    # 4. Test error handling on bad inputs
    print("\n--- Testing Error Handling on Bad Inputs ---")
    # Unsupported file extension
    res_bad_file = client.post(
        "/api/matches",
        files={"file": ("bad_file.txt", b"plain text content", "text/plain")}
    )
    assert res_bad_file.status_code == 400
    print("[PASS]: Rejected unsupported file extension (.txt) with status 400.")

    # Unknown match ID
    res_unknown = client.get("/api/matches/non_existent_123/results")
    assert res_unknown.status_code == 404
    print("[PASS]: Unknown match ID returned status 404.")

    # 5. Presentation backup verification
    print("\n--- Testing Presentation Backup ---")
    res_backup = client.get("/api/matches/backup_demo/results")
    assert res_backup.status_code == 200
    assert res_backup.json()["status"] == "completed"
    print("[PASS]: Backup demo report loads immediately for presentations.")

    print("\n==================================================")
    print("    ALL HOUR 4 ACCEPTANCE CRITERIA SATISFIED!     ")
    print("==================================================")


if __name__ == "__main__":
    run_hour_4_tests()
