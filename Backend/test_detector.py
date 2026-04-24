from dotenv import load_dotenv
import os
import requests
import base64

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

print("API Key loaded:", "✅ Yes" if ROBOFLOW_API_KEY else "❌ No")
print("Model ID:", MODEL_ID)
print("-" * 40)

# Correct base64 format for Roboflow
with open('download.jpg', 'rb') as f:
    image_data = f.read()

# Encode to base64 string
encoded = base64.b64encode(image_data).decode('ascii')

response = requests.post(
    f"https://detect.roboflow.com/{MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
    data=encoded,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

print("Status Code:", response.status_code)
print("Raw API Response:", response.json())