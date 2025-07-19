import os
import random
import shutil

# กำหนดโฟลเดอร์หลักบน Desktop
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "egg_counter_project")

# กำหนดโฟลเดอร์รูปและ label ต้นทาง (รวมไฟล์ทั้งหมด)
images_src = os.path.join(BASE_DIR, "dataset", "images_all")
labels_src = os.path.join(BASE_DIR, "dataset", "labels_all")  # ปรับชื่อโฟลเดอร์ตามของคุณ

# โฟลเดอร์ปลายทางสำหรับแบ่ง train/val
images_train = os.path.join(BASE_DIR, "dataset", "images", "train")
images_val = os.path.join(BASE_DIR, "dataset", "images", "val")
labels_train = os.path.join(BASE_DIR, "dataset", "labels", "train")
labels_val = os.path.join(BASE_DIR, "dataset", "labels", "val")


# อ่านชื่อไฟล์รูปภาพทั้งหมด (.jpg และ .png)
image_files = [f for f in os.listdir(images_src) if f.endswith('.jpg') or f.endswith('.png')]

# สุ่มไฟล์และแบ่งตามสัดส่วน
random.shuffle(image_files)
split_ratio = 0.8  # 80% train, 20% val
split_index = int(len(image_files) * split_ratio)

train_files = image_files[:split_index]
val_files = image_files[split_index:]

def move_files(file_list, img_src, lbl_src, img_dst, lbl_dst):
    for f in file_list:
        # คัดลอกไฟล์ภาพ
        shutil.copy(os.path.join(img_src, f), os.path.join(img_dst, f))
        # คัดลอกไฟล์ label ที่ตรงกัน (.txt)
        label_file = os.path.splitext(f)[0] + ".txt"
        shutil.copy(os.path.join(lbl_src, label_file), os.path.join(lbl_dst, label_file))

# ย้ายไฟล์ train
move_files(train_files, images_src, labels_src, images_train, labels_train)
# ย้ายไฟล์ val
move_files(val_files, images_src, labels_src, images_val, labels_val)

print(f"จำนวนไฟล์ train: {len(train_files)}")
print(f"จำนวนไฟล์ validation: {len(val_files)}")
