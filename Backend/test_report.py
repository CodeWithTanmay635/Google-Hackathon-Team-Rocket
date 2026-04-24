from damage_detector import detect_damage
from traffic_predictor import predict_traffic
from report_generator import generate_report

# Test with a real image
detection = detect_damage('download.jpg')
traffic = predict_traffic('market chowk', '9am')

# Generate report
report = generate_report(detection, 'Solapur, Maharashtra', traffic)

print(report['report_content'])
print("\n✅ Report saved to:", report['report_file'])