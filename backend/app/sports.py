"""
Sports configuration and court geometry definitions.
Member 4: Backend API Lead (Hours 6-8 Combined Team Plan)

Architecture:
- Badminton: Fully supported & validated end-to-end.
- Tennis & Squash: Architectural design directions sharing the same homography & player tracking pipeline.
"""

from typing import Dict, Any

SUPPORTED_SPORTS: Dict[str, Dict[str, Any]] = {
    "badminton": {
        "name": "Badminton",
        "status": "active",
        "court_dimensions_meters": {
            "length": 13.4,
            "singles_width": 5.18,
            "doubles_width": 6.1
        },
        "zones": [
            {"id": "front_court", "name": "Front Court (Net Area)", "y_range": [0.35, 0.65]},
            {"id": "mid_court", "name": "Mid Court", "y_range": [0.20, 0.80]},
            {"id": "back_court", "name": "Rear Court (Baseline)", "y_range": [0.0, 0.20, 0.80, 1.0]}
        ],
        "default_metrics": ["distance_m", "court_coverage", "rear_court_dist"]
    },
    "tennis": {
        "name": "Tennis",
        "status": "architecture_design_direction",
        "court_dimensions_meters": {
            "length": 23.77,
            "singles_width": 8.23,
            "doubles_width": 10.97
        },
        "default_metrics": ["distance_m", "court_coverage", "baseline_dominance"]
    },
    "squash": {
        "name": "Squash",
        "status": "architecture_design_direction",
        "court_dimensions_meters": {
            "length": 9.75,
            "width": 6.4
        },
        "default_metrics": ["distance_m", "t_dominance", "court_coverage"]
    }
}


def get_sport_info(sport_name: str = "badminton") -> Dict[str, Any]:
    return SUPPORTED_SPORTS.get(sport_name.lower(), SUPPORTED_SPORTS["badminton"])
