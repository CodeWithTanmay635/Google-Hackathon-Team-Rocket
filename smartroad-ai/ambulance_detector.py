import cv2
import numpy as np
from ultralytics import YOLO

class AmbulanceDetector:
    def __init__(self, model_path='yolov8n.pt'):
        """
        Initializes the Ambulance Detector using YOLOv8.
        """
        print(f"[INIT] Loading YOLO AI Model from {model_path}...")
        self.model = YOLO(model_path)
        
        # YOLO COCO dataset classes: 2 = car, 5 = bus, 7 = truck
        # Since standard YOLO doesn't have an "ambulance" class by default,
        # we classify generic vehicles and perform secondary color/feature filtering.
        self.vehicle_classes = [2, 5, 7] 
        print("[INIT] YOLOv8n initialized for <100ms inference.")
    
    def determine_lane(self, cx, cy, frame_width=1920, frame_height=1080):
        """
        Step 3: Determine Lane Position.
        Calculates which lane the ambulance is in based on bounding box centroid (cx, cy).
        Logic simulates physical intersection mapping.
        """
        center_x = frame_width / 2
        center_y = frame_height / 2
        
        # Vertical boundary tolerances for detecting East/West presence vs North/South
        if cy in range(int(center_y - 120), int(center_y + 120)):
            if cx < center_x:
                return "WEST"
            else:
                return "EAST"
        else:
            if cx < center_x:
                return "NORTH"
            else:
                return "SOUTH"

    def analyze_colors(self, vehicle_crop):
        """
        Secondary Filtering:
        Analyzes vehicle crop to calculate percentage of white and red pixels to identify ambulances.
        """
        if vehicle_crop.size == 0 or vehicle_crop.shape[0] == 0 or vehicle_crop.shape[1] == 0:
            return False, 0.0, 0.0
            
        hsv = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2HSV)
        
        # Define ranges for White pixels
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 50, 255])
        
        # Define ranges for Red pixels (wraps around 0-180 in OpenCV HSV)
        lower_red_1 = np.array([0, 100, 100])
        upper_red_1 = np.array([10, 255, 255])
        lower_red_2 = np.array([160, 100, 100])
        upper_red_2 = np.array([180, 255, 255])
        
        # Generate Masks
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        mask_red_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
        mask_red_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
        mask_red = cv2.bitwise_or(mask_red_1, mask_red_2)
        
        total_pixels = vehicle_crop.shape[0] * vehicle_crop.shape[1]
        if total_pixels == 0:
            return False, 0.0, 0.0
            
        white_pixels = cv2.countNonZero(mask_white)
        red_pixels = cv2.countNonZero(mask_red)
        
        white_pct = (white_pixels / total_pixels) * 100 
        red_pct = (red_pixels / total_pixels) * 100
        
        # Logic matching Presentation Step 2: Match WHITE + RED CROSS ✓
        # E.g., > 40% White and > 8% Red
        is_ambulance = (white_pct > 40.0) and (red_pct > 8.0)
        
        return is_ambulance, white_pct, red_pct

    def process_frame(self, frame):
        """
        Step 1 & 2: Data Ingestion and Inference filtering.
        Scans a video frame and returns a list of detected ambulances with telemetry data.
        """
        h, w = frame.shape[:2]
        
        # YOLO inference
        results = self.model(frame, verbose=False)[0]
        detected_ambulances = []
        
        for box in results.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Step 2: Filtering Engine -> Discard persons/irrelevant objects, keep generic vehicles
            if cls in self.vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Calculate centroids
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # Extract image crop for secondary analysis
                crop = frame[y1:y2, x1:x2]
                
                # Verify Ambulance signatures natively
                is_ambulance, white_pct, red_pct = self.analyze_colors(crop)
                
                if is_ambulance:
                    # Mathematical Lane computation mapping
                    lane = self.determine_lane(cx, cy, frame_width=w, frame_height=h)
                    
                    target_payload = {
                        "id": "AMBULANCE",
                        "bbox_coords": [x1, y1, x2, y2],
                        "confidence": round(conf * 100, 2),
                        "center": {"x": cx, "y": cy},
                        "dimensions": f"{x2-x1}x{y2-y1}px",
                        "color_analysis": {
                            "white_pixels_pct": round(white_pct, 1),
                            "red_pixels_pct": round(red_pct, 1),
                            "verified_match": True
                        },
                        "lane": lane
                    }
                    detected_ambulances.append(target_payload)
                    print(f"[DETECT] Confirmed AMBULANCE in {lane} LANE. Conf: {target_payload['confidence']}%")
        
        return detected_ambulances

# Example Usage mock
if __name__ == "__main__":
    print("Testing AmbulanceDetector initialization...")
    detector = AmbulanceDetector()
    # Mock behavior
    print("Test Logic: cy=540, cx=400 ->", detector.determine_lane(400, 540))
