"""
Verification test for Member 4's FastAPI endpoints (Hour 2).
"""

import time
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_hour_2_endpoints():
    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    print("[PASS] GET /api/health ->", res.json())

    # 2. Upload video
    with open("sample.mp4", "rb") as f:
        files = {"file": ("sample.mp4", f, "video/mp4")}
        res = client.post("/api/matches", files=files)
    assert res.status_code == 200
    match_data = res.json()
    match_id = match_data["match_id"]
    print(f"[PASS] POST /api/matches -> match_id={match_id}, status={match_data['status']}")

    # 3. Trigger analyze with 4 corners in order and court_type="doubles"
    court_corners = [[100, 40], [540, 40], [540, 320], [100, 320]]
    res = client.post(
        f"/api/matches/{match_id}/analyze",
        json={"sport": "badminton", "court_type": "doubles", "court_corners": court_corners}
    )
    assert res.status_code == 200
    print(f"[PASS] POST /api/matches/{match_id}/analyze ->", res.json())

    # 4. Check not-ready status / 409 response
    # 5. Poll status until completed
    for i in range(15):
        res = client.get(f"/api/matches/{match_id}/status")
        assert res.status_code == 200
        status_info = res.json()
        print(f"       Status poll #{i+1}: {status_info['status']}")
        if status_info["status"] == "completed":
            break
        time.sleep(1.0)

    # 6. Fetch results
    res = client.get(f"/api/matches/{match_id}/results")
    assert res.status_code == 200
    results = res.json()
    print(f"[PASS] GET /api/matches/{match_id}/results -> Duration: {results['duration_seconds']}s, Tracks: {len(results['tracks'])}, Metrics: {len(results['metrics'])}")

    # 7. Media streaming
    res = client.get(f"/media/{match_id}/video")
    assert res.status_code == 200
    print(f"[PASS] GET /media/{match_id}/video -> size: {len(res.content)} bytes")

    res = client.get(f"/media/{match_id}/annotated.mp4")
    assert res.status_code == 200
    print(f"[PASS] GET /media/{match_id}/annotated.mp4 -> size: {len(res.content)} bytes")

    print("\nALL MEMBER 4 HOUR 2 ENDPOINT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_hour_2_endpoints()
