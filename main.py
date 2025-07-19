import os
import cv2
import datetime
import numpy as np
from ultralytics import YOLO
from sort import Sort  # ต้องมีไฟล์ sort.py ในโปรเจคเดียวกัน

# กำหนด Base Dir ของโปรเจค
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "egg_counter_project")

# โฟลเดอร์เก็บไฟล์ CSV และภาพ
CSV_DIR = os.path.join(BASE_DIR, "logs", "device01", "csv")
IMG_DIR = os.path.join(BASE_DIR, "logs", "device01", "images")

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# ฟังก์ชันบันทึกข้อมูล
def save_data(frame, count_this_frame, total_count):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S-%f")

    csv_path = os.path.join(CSV_DIR, f"{date_str}.csv")
    img_path = os.path.join(IMG_DIR, f"{date_str}_{time_str}.png")

    print(f"บันทึกไฟล์รูปที่: {img_path}")
    cv2.imwrite(img_path, frame)

    print(f"บันทึกไฟล์ CSV ที่: {csv_path}")
    with open(csv_path, "a", encoding="utf-8") as f:
        f.write(f"{now.isoformat()},{count_this_frame},{total_count}\n")

    return img_path, csv_path

def main():
    # โหลดโมเดลที่เทรนเสร็จแล้ว (แก้ path ให้ถูกต้อง)
    model_path = os.path.join(BASE_DIR, "runs", "detect", "train3", "weights", "best.pt")
    model = YOLO(model_path)

    # เรียกใช้งาน Tracker SORT (ปรับ max_age ให้เก็บ track นานขึ้น)
    tracker = Sort(max_age=10, min_hits=1, iou_threshold=0.3)

    cap = cv2.VideoCapture(1)  # กล้อง 1
    if not cap.isOpened():
        print("ไม่สามารถเปิดกล้องได้")
        return

    total_count = 0
    counted_ids = set()  # เก็บ ID ที่นับไปแล้ว
    previous_positions = {}  # เก็บตำแหน่ง cx ก่อนหน้า ของแต่ละ track_id

    print("เริ่มจับภาพและนับไข่... กด 'q' เพื่อออก")

    # เส้นนับ (แนวตั้ง)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    line_x = frame_width // 2  # กึ่งกลางภาพ

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ไม่สามารถอ่านภาพจากกล้องได้")
            break

        # ตรวจจับวัตถุด้วย YOLO (ได้ผลลัพธ์แบบ list)
        results = model(frame)[0]

        # ดึง bounding boxes, confidence, class id
        detections = []
        for box, conf, cls in zip(results.boxes.xyxy, results.boxes.conf, results.boxes.cls):
            # กรองเฉพาะ class ไข่ (index 0 เพราะ train แค่ 1 class) และปรับ confidence threshold
            if int(cls) == 0 and conf > 0.3:
                x1, y1, x2, y2 = box.cpu().numpy()
                detections.append([x1, y1, x2, y2, conf.cpu().numpy()])

        # แปลงเป็น numpy array สำหรับ tracker
        dets = np.array(detections)
        if dets.shape[0] == 0:
            dets = np.empty((0, 5))

        # Update tracker และรับผลลัพธ์เป็น bbox + id
        tracks = tracker.update(dets)

        count_this_frame = 0

        for track in tracks:
            x1, y1, x2, y2, track_id = track
            x1, y1, x2, y2, track_id = int(x1), int(y1), int(x2), int(y2), int(track_id)
            cx = (x1 + x2) // 2

            # วาดกรอบสีเขียว และ id
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            # ตรวจสอบว่า track_id นี้เคยอยู่ฝั่งซ้าย (ก่อนหน้า) และตอนนี้ข้ามเส้นไปฝั่งขวาแล้วหรือยัง
            prev_cx = previous_positions.get(track_id, None)
            if prev_cx is not None:
                if prev_cx < line_x <= cx and track_id not in counted_ids:
                    total_count += 1
                    count_this_frame += 1
                    counted_ids.add(track_id)
            # บันทึกตำแหน่งปัจจุบัน
            previous_positions[track_id] = cx

        # วาดเส้นนับ (แนวตั้ง)
        cv2.line(frame, (line_x, 0), (line_x, frame.shape[0]), (255, 0, 0), 3)

        # แสดงจำนวนไข่
        cv2.putText(frame, f"Total Eggs: {total_count}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)

        # บันทึกข้อมูล
        if count_this_frame > 0:
            save_data(frame, count_this_frame, total_count)

        cv2.imshow("Egg Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("ออกจากโปรแกรมแล้ว")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
