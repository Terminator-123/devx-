"""
End-to-end pipeline verification test.
Tests Member 1 vision pipeline and Member 4 backend schemas together.
"""

import os
import json
from app.vision.video import analyze_video
from app.schemas import MatchResultsResponse

def test_full_pipeline():
    sample_video = "sample.mp4"
    if not os.path.exists(sample_video):
        from create_sample_clip import create_sample_video
        create_sample_video(sample_video)

    print("Running analyze_video on sample.mp4...")
    result = analyze_video(
        video_path=sample_video,
        sport="badminton",
        court_corners=[[100, 40], [540, 40], [540, 320], [100, 320]]
    )

    print("\n--- Pipeline Result Keys ---")
    print(list(result.keys()))

    print(f"\nStatus: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds')}s")
    print(f"Metrics count: {len(result.get('metrics', []))}")
    for m in result.get('metrics', []):
        print(f"  - {m['label']}: {m['value']} {m['unit']} (conf: {m['confidence']})")

    print(f"Events count: {len(result.get('events', []))}")
    for e in result.get('events', []):
        print(f"  - [{e['start_seconds']}s - {e['end_seconds']}s] {e['title']}")

    print(f"Tracks count: {len(result.get('tracks', []))}")
    print(f"Heatmap bins count: {len(result.get('heatmap', []))}")

    # Validate schema compatibility with Member 4's MatchResultsResponse
    validated = MatchResultsResponse(match_id="test-1", **result)
    print("\n[SUCCESS] Result perfectly matches Member 4's Pydantic schema!")
    return True

if __name__ == "__main__":
    test_full_pipeline()
