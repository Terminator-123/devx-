# Save as test_model.py; place clip at backend/sample.mp4
import os
import cv2
from ultralytics import YOLO

clip_path = "sample.mp4" if os.path.exists("sample.mp4") else "backend/sample.mp4"
if not os.path.exists(clip_path):
    import sys
    sys.path.append(os.path.dirname(__file__))
    from create_sample_clip import create_sample_video
    create_sample_video(clip_path)

cap = cv2.VideoCapture(clip_path)
ok, frame = cap.read()
cap.release()
if not ok:
    raise RuntimeError(f"Cannot read {clip_path}")

cv2.imwrite("frame.jpg", frame)
print("Saved frame to frame.jpg")

model = YOLO("yolov8n.pt")
results = model.predict("frame.jpg", imgsz=640, conf=0.25, save=True)
print("Inference completed successfully!")
for r in results:
    print(f"Detected {len(r.boxes)} bounding boxes.")
