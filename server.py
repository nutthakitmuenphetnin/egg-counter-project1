from flask import Flask, send_from_directory, jsonify
import os
import csv
from datetime import datetime

app = Flask(__name__, static_folder="frontend", static_url_path='')

# 1. Serve HTML หน้าแรก
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# 2. API: ส่งข้อมูล CSV + ชื่อไฟล์ล่าสุด + ชื่อรูปภาพล่าสุด
@app.route('/data')
def send_data():
    logs_folder = 'logs/device01'
    csv_files = [f for f in os.listdir(logs_folder) if f.endswith('.csv')]
    image_files = [f for f in os.listdir(logs_folder) if f.endswith('.png')]

    if not csv_files:
        return jsonify({"error": "No CSV files found"}), 404

    latest_csv = sorted(csv_files)[-1]
    latest_csv_path = os.path.join(logs_folder, latest_csv)

    # อ่านข้อมูล CSV
    data = []
    with open(latest_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # ข้าม header ถ้ามี
        for row in reader:
            data.append(row)

    # หาไฟล์รูปภาพล่าสุด (ตาม timestamp filename)
    latest_image = sorted(image_files)[-1] if image_files else None

    return jsonify({
        "csv_data": {
            "filename": latest_csv,
            "data": data
        },
        "latest_image": latest_image
    })

# 3. Serve รูปภาพจาก logs/device01
@app.route('/logs/device01/<path:filename>')
def serve_logs_file(filename):
    return send_from_directory('logs/device01', filename)

# 4. รัน Flask App
if __name__ == '__main__':
    app.run(debug=True)

