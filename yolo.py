import os
import xml.etree.ElementTree as ET

# กำหนดโฟลเดอร์หลักบน Desktop
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "egg_counter_project")
xml_folder = os.path.join(BASE_DIR, "egg_taining")
txt_folder = os.path.join(BASE_DIR, "labels")

# สร้างโฟลเดอร์ labels หากยังไม่มี
os.makedirs(txt_folder, exist_ok=True)

# กำหนดชื่อคลาสที่ต้องการ (แก้ได้ตามจำนวนคลาสจริงของคุณ)
classes = ["egg"]  # ถ้ามีหลายคลาส เช่น ["egg", "chicken", "duck"]

def convert_bbox(size, box):
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    xmin, xmax, ymin, ymax = box
    x = (xmin + xmax) / 2.0
    y = (ymin + ymax) / 2.0
    w = xmax - xmin
    h = ymax - ymin
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def convert_annotation(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    yolo_labels = []

    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in classes:
            continue
        cls_id = classes.index(cls)

        xmlbox = obj.find('bndbox')
        xmin = float(xmlbox.find('xmin').text)
        ymin = float(xmlbox.find('ymin').text)
        xmax = float(xmlbox.find('xmax').text)
        ymax = float(xmlbox.find('ymax').text)

        bb = (xmin, xmax, ymin, ymax)
        yolo_bbox = convert_bbox((w, h), bb)
        yolo_labels.append(f"{cls_id} {' '.join(format(a, '.6f') for a in yolo_bbox)}")

    return yolo_labels

def main():
    xml_files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]

    for xml_file in xml_files:
        xml_path = os.path.join(xml_folder, xml_file)
        yolo_labels = convert_annotation(xml_path)

        txt_filename = os.path.splitext(xml_file)[0] + ".txt"
        txt_path = os.path.join(txt_folder, txt_filename)

        with open(txt_path, 'w') as f:
            f.write("\n".join(yolo_labels))
        print(f"แปลง {xml_file} -> {txt_filename}")

if __name__ == "__main__":
    main()
