import os

BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "egg_counter_project")
data_yaml_path = os.path.join(BASE_DIR, "egg_data.yaml")

from ultralytics import YOLO

model = YOLO('yolov8s.pt')
model.train(data=data_yaml_path, epochs=50, imgsz=640, batch=16)
