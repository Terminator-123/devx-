"""
Court calibration module for Badminton.
Maps 2D pixel coordinates from camera view to normalized 2D court space [0, 1]
and real-world coordinates in meters (13.4m x 6.1m for doubles, 13.4m x 5.18m for singles).
"""

from typing import List, Optional, Tuple
import numpy as np
import cv2

COURT_LENGTH_M = 13.4
DOUBLES_WIDTH_M = 6.1
SINGLES_WIDTH_M = 5.18


class CourtCalibrator:
    def __init__(
        self,
        court_corners: Optional[List[List[float]]] = None,
        frame_size: Optional[Tuple[int, int]] = None,
        court_type: str = "doubles"
    ):
        """
        court_corners: 4 points in order: top-left, top-right, bottom-right, bottom-left
        frame_size: (width, height)
        court_type: 'doubles' (6.1m) or 'singles' (5.18m)
        """
        self.frame_width = frame_size[0] if frame_size else 1280
        self.frame_height = frame_size[1] if frame_size else 720
        self.court_type = court_type.lower() if court_type else "doubles"
        self.court_width_m = SINGLES_WIDTH_M if "single" in self.court_type else DOUBLES_WIDTH_M
        self.court_length_m = COURT_LENGTH_M

        self.homography_matrix = None
        self.is_valid = False

        if court_corners and len(court_corners) == 4:
            self._compute_homography(court_corners)

    def _compute_homography(self, corners: List[List[float]]):
        try:
            src_pts = np.array(corners, dtype=np.float32)
            # Destination: normalized court space [0, 1] x [0, 1]
            # Order: top-left, top-right, bottom-right, bottom-left
            dst_pts = np.array([
                [0.0, 0.0],
                [1.0, 0.0],
                [1.0, 1.0],
                [0.0, 1.0]
            ], dtype=np.float32)
            H, _ = cv2.findHomography(src_pts, dst_pts)
            if H is not None:
                self.homography_matrix = H
                self.is_valid = True
        except Exception:
            self.homography_matrix = None
            self.is_valid = False

    def map_point(self, x: float, y: float) -> Optional[Tuple[float, float]]:
        """
        Maps (x, y) pixel coordinates to normalized court coordinates (0.0 to 1.0)
        when calibration is valid. Returns None if calibration is invalid.
        """
        if self.is_valid and self.homography_matrix is not None:
            pt = np.array([[[x, y]]], dtype=np.float32)
            transformed = cv2.perspectiveTransform(pt, self.homography_matrix)
            nx = float(np.clip(transformed[0][0][0], 0.0, 1.0))
            ny = float(np.clip(transformed[0][0][1], 0.0, 1.0))
            return nx, ny
        return None

    def court_to_meters(self, nx: float, ny: float) -> Tuple[float, float]:
        """
        Converts normalized court coords to meters: (x_m, y_m)
        """
        return nx * self.court_width_m, ny * self.court_length_m
