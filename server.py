from flask import Flask, jsonify, send_from_directory, request, send_file
import os
import glob
import csv
import datetime

app = Flask(__name__)

BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "egg_counter_project")
CSV_DIR = os.path.join(BASE_DIR, "logs", "device01", "csv")
IMG_DIR = os.path.join(BASE_DIR, "logs", "device01", "images")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def get_latest_csv():
    csv_files = glob.glob(os.path.join(CSV_DIR, "*.csv"))
    if not csv_files:
        return {}
    latest_csv = max(csv_files, key=os.path.getmtime)
    data = []
    with open(latest_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return {
        "filename": os.path.basename(latest_csv),
        "data": data
    }

def get_latest_image():
    img_files = glob.glob(os.path.join(IMG_DIR, "*.png"))
    if not img_files:
        return None
    latest_img = max(img_files, key=os.path.getmtime)
    return os.path.basename(latest_img)

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/data')
def data():
    csv_data = get_latest_csv()
    latest_img = get_latest_image()
    return jsonify({
        "csv_data": csv_data,
        "latest_image": latest_img
    })

@app.route('/images/<filename>')
def images(filename):
    return send_from_directory(IMG_DIR, filename)

# เปลี่ยน /save_csv เป็น /download_csv ให้ดาวน์โหลดไฟล์ CSV ล่าสุด
@app.route('/download_csv', methods=['GET'])
def download_csv():
    csv_files = glob.glob(os.path.join(CSV_DIR, "*.csv"))
    if not csv_files:
        return jsonify({"status": "error", "message": "No CSV files found"}), 400
    latest_csv = max(csv_files, key=os.path.getmtime)
    return send_file(latest_csv, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
