import tkinter as tk
import requests
import threading
import time
from PIL import Image, ImageTk
from io import BytesIO

# URL API ของ backend Flask server
API_URL = "http://127.0.0.1:5000/data"
IMAGE_BASE_URL = "http://127.0.0.1:5000/images/"

class EggCounterUI:
    def __init__(self, root):
        self.root = root
        root.title("Egg Counter UI")

        # หัวข้อ
        self.label_title = tk.Label(root, text="จำนวนไข่ทั้งหมด", font=("Arial", 24))
        self.label_title.pack(pady=10)

        # แสดงจำนวนไข่
        self.count_var = tk.StringVar(value="0")
        self.label_count = tk.Label(root, textvariable=self.count_var, font=("Arial", 48), fg="blue")
        self.label_count.pack(pady=20)

        # แสดงภาพล่าสุด
        self.image_label = tk.Label(root)
        self.image_label.pack()

        # เริ่มดึงข้อมูลและอัพเดต UI ทุก 2 วินาที
        self.update_data()

    def update_data(self):
        def task():
            try:
                response = requests.get(API_URL, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    count = 0
                    if "csv_data" in data and data["csv_data"]:
                        rows = data["csv_data"].get("data", [])
                        if rows:
                            # สมมติข้อมูล csv มีบรรทัดล่าสุดเป็น count ล่าสุด
                            last_line = rows[-1]
                            if len(last_line) >= 3:
                                count = int(last_line[2])

                    self.count_var.set(str(count))

                    # โหลดภาพล่าสุดถ้ามี
                    img_name = data.get("latest_image")
                    if img_name:
                        img_url = IMAGE_BASE_URL + img_name
                        img_resp = requests.get(img_url, timeout=3)
                        if img_resp.status_code == 200:
                            image_data = img_resp.content
                            pil_image = Image.open(BytesIO(image_data))
                            pil_image = pil_image.resize((400, 300))  # ปรับขนาดตามต้องการ
                            tk_image = ImageTk.PhotoImage(pil_image)

                            # ต้องเก็บ ref ไม่งั้นภาพหาย
                            self.image_label.imgtk = tk_image
                            self.image_label.configure(image=tk_image)
                        else:
                            self.image_label.configure(image='')

                else:
                    print(f"Error fetching data: {response.status_code}")
            except Exception as e:
                print(f"Exception fetching data: {e}")

            # เรียก update_data ซ้ำหลัง 2 วินาที
            self.root.after(2000, self.update_data)

        # รัน task ใน thread เพื่อไม่ให้ UI ค้าง
        threading.Thread(target=task).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = EggCounterUI(root)
    root.mainloop()
