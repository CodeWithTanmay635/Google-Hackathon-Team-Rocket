from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from damage_detector import detect_damage
from traffic_predictor import predict_traffic
from report_generator import generate_report
from live_monitor import generate_frames
import os
import glob
import cv2
import numpy as np

# ✅ Import EV Priority Modules Safely
try:
    from ambulance_detector import AmbulanceDetector
    from signal_controller import TrafficSignalController
    from route_optimizer import RouteOptimizer
    ev_detector = AmbulanceDetector()
    signal_ctrl = TrafficSignalController()
    route_opt = RouteOptimizer()
    print("[SYSTEM] EV Priority Modules Loaded Successfully.")
except Exception as e:
    print(f"[WARNING] EV Modules failed to load: {e}")
    ev_detector = None
    signal_ctrl = None
    route_opt = None

app = Flask(__name__)
CORS(app)

# ✅ Serve Frontend Pages
@app.route('/')
def home():
    return send_from_directory('../Frontend', 'index.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    # Only serve html, css, js files
    if filename.endswith(('.html', '.css', '.js', '.png', '.jpg', '.ico')):
        return send_from_directory('../Frontend', filename)
    return jsonify({'error': 'Not found'}), 404

# ✅ Detect Route
@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    image_path = 'temp_input.jpg'
    image.save(image_path)

    result = detect_damage(image_path)
    return jsonify(result)

# ✅ Traffic Route
@app.route('/traffic', methods=['POST'])
def traffic():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    area = data.get('area', '')
    time = data.get('time', '')

    if not area or not time:
        return jsonify({'error': 'Area and time required'}), 400

    result = predict_traffic(area, time)
    return jsonify(result)

# ✅ Report Route
@app.route('/report', methods=['POST'])
def report():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    detection_result = data.get('detection_result', {})
    location = data.get('location', 'Solapur, Maharashtra')
    traffic_result = data.get('traffic_result', None)

    result = generate_report(detection_result, location, traffic_result)
    return jsonify(result)

# ✅ Live Stream Route
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ✅ Reports API Routes
@app.route('/api/reports', methods=['GET'])
def get_reports():
    reports_dir = 'reports'
    if not os.path.exists(reports_dir):
        return jsonify([])
    
    report_files = glob.glob(os.path.join(reports_dir, 'SR-*.txt'))
    # Sort files by modification time descending
    report_files.sort(key=os.path.getmtime, reverse=True)
    
    reports_list = []
    for filepath in report_files:
        filename = os.path.basename(filepath)
        # Extract basic info
        stats = os.stat(filepath)
        reports_list.append({
            'filename': filename,
            'id': filename.replace('.txt', ''),
            'timestamp': stats.st_mtime
        })
    
    return jsonify(reports_list)

@app.route('/api/reports/<filename>', methods=['GET'])
def get_report_content(filename):
    return send_from_directory('reports', filename)

# ✅ Status Route - check if backend alive
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'message': 'SmartRoad AI Backend Running 🚀',
        'routes': ['/detect', '/traffic', '/report', '/status', '/video_feed', '/api/reports']
    })

# ✅ EV Priority System API Integrations
@app.route('/api/emergency/detect_frame', methods=['POST'])
def emergency_detect():
    if not ev_detector:
        return jsonify({'error': 'EV Detector offline'}), 503
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    file_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({'error': 'Invalid image format'}), 400

    detections = ev_detector.process_frame(frame)
    return jsonify(detections)

@app.route('/api/emergency/signal_status', methods=['GET'])
def signal_status():
    if not signal_ctrl: return jsonify({'error': 'Offline'}), 503
    return jsonify(signal_ctrl.get_status())

@app.route('/api/emergency/priority', methods=['POST'])
def set_priority():
    if not signal_ctrl: return jsonify({'error': 'Offline'}), 503
    data = request.get_json() or {}
    lane = data.get('lane')
    action = data.get('action') # 'activate' or 'deactivate'

    if action == 'activate' and lane:
        state = signal_ctrl.activate_priority(lane)
    elif action == 'deactivate':
        state = signal_ctrl.deactivate_priority()
    else:
        return jsonify({'error': 'Invalid action or missing lane payload'}), 400

    return jsonify(state)

@app.route('/api/emergency/route', methods=['POST'])
def optimize_route():
    if not route_opt: return jsonify({'error': 'Offline'}), 503
    data = request.get_json() or {}
    lat = data.get('lat', 17.6530)
    lon = data.get('lon', 75.9010)
    
    target = route_opt.find_nearest_hospital((float(lat), float(lon)))
    return jsonify(target)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)