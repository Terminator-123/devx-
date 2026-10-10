"""
Minute 60 End-to-End Integration Verification Test
Tests full cycle: upload -> analyze -> status -> results -> evidence replay
"""

import time
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_minute_60_test():
    print("==================================================")
    print("   RUNNING MINUTE 60 END-TO-END INTEGRATION TEST  ")
    print("==================================================")

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200 and res.json() == {"status": "ok"}
    print("Step 1 [PASS]: Health check confirmed API is running.")

    # 2. Upload video
    with open("sample.mp4", "rb") as f:
        res = client.post("/api/matches", files={"file": ("badminton_demo.mp4", f, "video/mp4")})
    assert res.status_code == 200
    match_id = res.json()["match_id"]
    print(f"Step 2 [PASS]: Video uploaded -> Match ID: {match_id}")

    # 3. Start analysis with 4 calibrated corners (TL, TR, BR, BL)
    corners = [[100, 40], [540, 40], [540, 320], [100, 320]]
    res = client.post(
        f"/api/matches/{match_id}/analyze",
        json={"sport": "badminton", "court_type": "doubles", "court_corners": corners}
    )
    assert res.status_code == 200
    print(f"Step 3 [PASS]: Analysis started with 4-corner calibration.")

    # 4. Poll status
    completed = False
    for attempt in range(20):
        res = client.get(f"/api/matches/{match_id}/status")
        st = res.json()["status"]
        if st == "completed":
            completed = True
            print(f"Step 4 [PASS]: Job completed successfully (poll attempt {attempt+1}).")
            break
        time.sleep(1.0)
    assert completed, "Job did not complete within expected time"

    # 5. Fetch completed report
    res = client.get(f"/api/matches/{match_id}/results")
    assert res.status_code == 200
    data = res.json()
    print("Step 5 [PASS]: Results fetched successfully:")
    print(f"       - Duration: {data.get('duration_seconds')}s")
    print(f"       - Players tracked: {len(data.get('tracks', []))}")
    print(f"       - Metric cards: {[m['label'] + ': ' + str(m['value']) + ' ' + m['unit'] for m in data.get('metrics', [])]}")
    print(f"       - Heatmap cells: {len(data.get('heatmap', {}).get('cells', []))}")
    print(f"       - Events detected: {len(data.get('events', []))}")

    # 6. Verify evidence timestamp seeking / media stream
    assert len(data.get('events', [])) > 0, "At least one event required for evidence replay"
    first_event = data['events'][0]
    seek_ts = first_event['start_seconds']
    print(f"Step 6 [PASS]: Evidence replay validated -> Event '{first_event['title']}' targets {seek_ts}s.")

    # Media stream checks
    res_raw = client.get(f"/media/{match_id}/video")
    assert res_raw.status_code == 200
    res_annot = client.get(f"/media/{match_id}/annotated.mp4")
    assert res_annot.status_code == 200
    print(f"       - Raw video stream available ({len(res_raw.content)} bytes)")
    print(f"       - Annotated video stream available ({len(res_annot.content)} bytes)")

    print("\n==================================================")
    print("   ALL MINUTE 60 INTEGRATION REQUIREMENTS PASSED! ")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_minute_60_test()
