from ultralytics import YOLO

# This will download YOLOv8 nano model automatically
model = YOLO('yolov8n.pt')
print("✅ YOLO is working perfectly!")