from dotenv import load_dotenv
import os
import requests
import base64

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

# Minimum confidence threshold - only accept above this
CONFIDENCE_THRESHOLD = 0.70

def detect_damage(image_path):
    if not os.path.exists(image_path):
        return {
            'damage_found': False,
            'detections': [],
            'error': 'Image not found'
        }

    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = f.read()

    encoded = base64.b64encode(image_data).decode('ascii')

    # Call Roboflow API
    response = requests.post(
        f"https://detect.roboflow.com/{MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    result = response.json()

    # Check for API errors
    if 'message' in result:
        return {
            'damage_found': False,
            'detections': [],
            'error': result['message']
        }

    detections = []
    rejected = 0

    for prediction in result.get('predictions', []):
        confidence = prediction['confidence']

        # Only accept detections above threshold
        if confidence >= CONFIDENCE_THRESHOLD:
            detections.append({
                'class': prediction['class'],
                'confidence': round(confidence * 100, 2),
                'severity': get_severity(confidence)
            })
        else:
            rejected += 1

    return {
        'damage_found': len(detections) > 0,
        'total_detections': len(detections),
        'detections': detections,
        'rejected_low_confidence': rejected,
        'threshold_used': f"{int(CONFIDENCE_THRESHOLD * 100)}%",
        'image_path': image_path
    }

def get_severity(confidence):
    if confidence > 0.85:
        return 'Critical'
    elif confidence > 0.75:
        return 'High'
    elif confidence > 0.70:
        return 'Medium'
    else:
        return 'Low'