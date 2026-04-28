import cv2
import time
import os
from datetime import datetime
from damage_detector import detect_damage
from report_generator import generate_report

# How many seconds between each detection check
DETECTION_INTERVAL = 5

def save_frame(frame):
    filename = f"temp_frame_{datetime.now().strftime('%H%M%S')}.jpg"
    cv2.imwrite(filename, frame)
    return filename

def draw_status(frame, message, color=(0, 255, 0)):
    cv2.putText(
        frame, message,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8, color, 2
    )
    return frame

def start_monitoring(location="Solapur, Maharashtra"):
    print("🚀 SmartRoad AI - Live Monitor Starting...")
    print("📷 Opening camera...")
    print("⏹️  Press 'Q' to quit\n")

    # Open laptop webcam (0 = default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Could not open camera!")
        return

    print("✅ Camera opened successfully!")

    last_detection_time = 0
    last_result = None
    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("❌ Failed to read frame!")
            break

        current_time = time.time()
        frame_count += 1

        # Run detection every DETECTION_INTERVAL seconds
        if current_time - last_detection_time >= DETECTION_INTERVAL:
            print(f"\n🔍 Running detection at {datetime.now().strftime('%H:%M:%S')}...")

            # Save current frame temporarily
            temp_file = save_frame(frame)

            # Run pothole detection
            result = detect_damage(temp_file)
            last_result = result
            last_detection_time = current_time

            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)

            if result['damage_found']:
                print(f"⚠️  POTHOLE DETECTED! {result['total_detections']} potholes found!")

                # Auto generate report
                report = generate_report(result, location)
                print(f"📋 Report saved: {report['report_file']}")
            else:
                print("✅ No damage detected")

        # Show status on live feed
        if last_result:
            if last_result['damage_found']:
                msg = f"⚠ POTHOLE DETECTED: {last_result['total_detections']} found!"
                frame = draw_status(frame, msg, color=(0, 0, 255))
            else:
                frame = draw_status(frame, "✅ Road Clear", color=(0, 255, 0))
        else:
            frame = draw_status(frame, "🔍 Initializing...", color=(255, 255, 0))

        # Show countdown to next detection
        time_left = int(DETECTION_INTERVAL - (current_time - last_detection_time))
        cv2.putText(
            frame,
            f"Next scan in: {time_left}s",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (255, 255, 255), 1
        )

        # Show live feed window
        cv2.imshow("SmartRoad AI - Live Monitor", frame)

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n⏹️  Monitoring stopped by user")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Camera released. Goodbye!")

def generate_frames(location="Solapur, Maharashtra"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return

    last_detection_time = 0
    last_result = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        if current_time - last_detection_time >= DETECTION_INTERVAL:
            temp_file = save_frame(frame)
            result = detect_damage(temp_file)
            last_result = result
            last_detection_time = current_time

            if os.path.exists(temp_file):
                os.remove(temp_file)

            if result['damage_found']:
                generate_report(result, location)

        if last_result:
            if last_result['damage_found']:
                msg = f"⚠ POTHOLE DETECTED: {last_result['total_detections']} found!"
                frame = draw_status(frame, msg, color=(0, 0, 255))
            else:
                frame = draw_status(frame, "✅ Road Clear", color=(0, 255, 0))
        else:
            frame = draw_status(frame, "🔍 Initializing...", color=(255, 255, 0))

        time_left = int(DETECTION_INTERVAL - (current_time - last_detection_time))
        cv2.putText(
            frame,
            f"Next scan in: {time_left}s",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (255, 255, 255), 1
        )

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

if __name__ == '__main__':
    start_monitoring(location="Solapur, Maharashtra")