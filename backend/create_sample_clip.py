"""
Utility to generate a test badminton video clip (sample.mp4)
with badminton court lines and players for CPU testing.
"""

import cv2
import numpy as np

def create_sample_video(output_path="sample.mp4", duration_sec=5, fps=25, width=640, height=360):
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    if not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = int(duration_sec * fps)
    court_color = (40, 140, 60)  # Green badminton court mat
    line_color = (255, 255, 255)

    for i in range(total_frames):
        t = i / fps
        frame = np.full((height, width, 3), (30, 30, 30), dtype=np.uint8)

        # Court boundary
        c_left, c_right = 100, 540
        c_top, c_bottom = 40, 320
        cv2.rectangle(frame, (c_left, c_top), (c_right, c_bottom), court_color, -1)
        cv2.rectangle(frame, (c_left, c_top), (c_right, c_bottom), line_color, 2)

        # Net line across midcourt
        net_y = int((c_top + c_bottom) / 2)
        cv2.line(frame, (c_left - 10, net_y), (c_right + 10, net_y), (220, 220, 220), 3)

        # Singles sideline & service lines
        cv2.line(frame, (c_left + 25, c_top), (c_left + 25, c_bottom), line_color, 1)
        cv2.line(frame, (c_right - 25, c_top), (c_right - 25, c_bottom), line_color, 1)
        cv2.line(frame, (c_left, net_y - 45), (c_right, net_y - 45), line_color, 1)
        cv2.line(frame, (c_left, net_y + 45), (c_right, net_y + 45), line_color, 1)

        # Player 1 (near court / bottom): moves left and right dynamically
        p1_x = int(320 + 85 * np.sin(t * 2.2))
        p1_y = int(255 + 20 * np.cos(t * 1.8))
        # Draw player silhouette (head + body + limbs)
        cv2.circle(frame, (p1_x, p1_y - 45), 11, (230, 190, 160), -1)  # Head
        cv2.rectangle(frame, (p1_x - 14, p1_y - 34), (p1_x + 14, p1_y), (0, 0, 220), -1)  # Red Jersey
        cv2.line(frame, (p1_x - 7, p1_y), (p1_x - 9, p1_y + 26), (40, 40, 40), 5)  # Left Leg
        cv2.line(frame, (p1_x + 7, p1_y), (p1_x + 9, p1_y + 26), (40, 40, 40), 5)  # Right Leg
        # Racket & Arm
        cv2.line(frame, (p1_x + 10, p1_y - 20), (p1_x + 28, p1_y - 40), (200, 200, 200), 2)
        cv2.circle(frame, (p1_x + 32, p1_y - 44), 9, (200, 200, 200), 1)

        # Player 2 (far court / top): moves across top half
        p2_x = int(320 - 75 * np.sin(t * 2.0))
        p2_y = int(115 + 16 * np.cos(t * 1.9))
        cv2.circle(frame, (p2_x, p2_y - 35), 9, (230, 190, 160), -1)
        cv2.rectangle(frame, (p2_x - 11, p2_y - 26), (p2_x + 11, p2_y), (220, 120, 20), -1)  # Blue Jersey
        cv2.line(frame, (p2_x - 5, p2_y), (p2_x - 7, p2_y + 22), (40, 40, 40), 4)
        cv2.line(frame, (p2_x + 5, p2_y), (p2_x + 7, p2_y + 22), (40, 40, 40), 4)

        # Shuttlecock flight trail
        shuttle_x = int(320 + 80 * np.cos(t * 3.5))
        shuttle_y = int(185 + 65 * np.sin(t * 3.5))
        cv2.circle(frame, (shuttle_x, shuttle_y), 3, (255, 255, 255), -1)

        out.write(frame)

    out.release()
    print(f"Sample clip created at {output_path}")

if __name__ == "__main__":
    create_sample_video()
