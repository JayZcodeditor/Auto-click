from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import pyautogui
import mouse
import time
import os
import threading

class AutoClickApp(App):
    def build(self):
        self.click_positions = []  # เก็บตำแหน่งที่บันทึกไว้
        self.is_clicked = False  # ตัวแปรสถานะเพื่อตรวจสอบการคลิกซ้าย
        self.is_listening = False  # ตัวแปรสถานะสำหรับการฟังการคลิกซ้าย

        # กำหนดเส้นทางของฟอนต์
        font_path = os.path.join(os.path.dirname(__file__), 'font', 'Kanit-SemiBold.ttf')

        # สร้าง layout หลักสำหรับจัดเรียง row
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Row แรก: Scrollable area สำหรับแสดงพิกัดที่บันทึก
        self.label = Label(text="กด 'เริ่มการบันทึกพิกัด' เพื่อเริ่มบันทึกพิกัดจากการคลิกซ้าย", 
                           font_size=18, font_name=font_path, size_hint_y=None, height=500, valign="top")
        self.label.bind(texture_size=self.label.setter('size'))
        
        scroll_view = ScrollView(size_hint=(1, 0.7))
        scroll_view.add_widget(self.label)
        main_layout.add_widget(scroll_view)

        # Row ที่สอง: ปุ่ม 4 ปุ่มในแนวนอน
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.3))
        
        # ปุ่มสำหรับเริ่มการบันทึกพิกัด
        self.start_record_button = Button(text="เริ่มการบันทึกพิกัด", font_size=18, font_name=font_path)
        self.start_record_button.bind(on_press=self.start_recording)

        # ปุ่มสำหรับยกเลิกการบันทึกพิกัด
        self.stop_record_button = Button(text="ยกเลิกการบันทึกพิกัด", font_size=18, font_name=font_path)
        self.stop_record_button.bind(on_press=self.stop_recording)
        self.stop_record_button.disabled = True  # ปิดการใช้งานปุ่มนี้ในตอนแรก

        # ปุ่มสำหรับรีเซ็ตการบันทึกตำแหน่ง
        self.reset_button = Button(text="รีเซ็ตพิกัด", font_size=18, font_name=font_path)
        self.reset_button.bind(on_press=self.reset_positions)

        # ปุ่มสำหรับเริ่มการคลิกอัตโนมัติ (ซ่อนปุ่มนี้ในตอนแรก)
        self.start_button = Button(text="เริ่มคลิกอัตโนมัติ", font_size=18, font_name=font_path)
        self.start_button.bind(on_press=self.start_auto_click)
        self.start_button.disabled = True  # ปิดการใช้งานปุ่มในตอนแรก

        # เพิ่มปุ่มทั้งหมดลงใน button_layout
        button_layout.add_widget(self.start_record_button)
        button_layout.add_widget(self.stop_record_button)
        button_layout.add_widget(self.reset_button)
        button_layout.add_widget(self.start_button)
        
        # เพิ่มทั้งสอง row ลงใน main_layout
        main_layout.add_widget(button_layout)
        
        # เริ่มการอัปเดตตำแหน่งเมาส์แบบเรียลไทม์
        Clock.schedule_interval(self.update_mouse_position, 0.1)

        return main_layout

    def start_recording(self, instance):
        # เริ่มการฟังการคลิกซ้าย
        self.is_listening = True
        self.label.text = "โปรดคลิกซ้ายบนหน้าจอเพื่อบันทึกพิกัด"
        self.start_record_button.disabled = True  # ปิดการใช้งานปุ่มเริ่มการบันทึกพิกัด
        self.stop_record_button.disabled = False  # เปิดการใช้งานปุ่มยกเลิกการบันทึกพิกัด
        # เริ่มการฟังคลิกซ้ายใน Thread แยก
        threading.Thread(target=self.listen_for_clicks, daemon=True).start()

    def stop_recording(self, instance):
        # ยกเลิกการฟังการบันทึกพิกัด
        self.is_listening = False
        self.label.text = f"ยกเลิกการบันทึกพิกัดแล้ว บันทึกทั้งหมด {len(self.click_positions)} ครั้ง"
        self.start_record_button.disabled = False  # เปิดการใช้งานปุ่มเริ่มการบันทึกพิกัดอีกครั้ง
        self.stop_record_button.disabled = True  # ปิดการใช้งานปุ่มยกเลิกการบันทึกพิกัด
        self.start_button.disabled = False  # เปิดใช้งานปุ่มเริ่มคลิกอัตโนมัติ

    def update_mouse_position(self, dt):
        # อัปเดตตำแหน่งเมาส์แบบเรียลไทม์
        x, y = pyautogui.position()
        positions_text = "\n".join([f"การคลิกครั้งที่ {i+1}: ({px}, {py})" for i, (px, py) in enumerate(self.click_positions)])
        self.label.text = f"ตำแหน่งเมาส์: ({x}, {y})\n{positions_text}"

    def listen_for_clicks(self):
        # ฟังก์ชันฟังการคลิกซ้ายทั่วทั้งหน้าจอ
        while self.is_listening:
            if mouse.is_pressed(button="left") and not self.is_clicked:
                # ตรวจจับการคลิกซ้ายครั้งเดียว
                self.is_clicked = True
                self.record_position()
            elif not mouse.is_pressed(button="left"):
                # รีเซ็ตสถานะการคลิกเมื่อปล่อยปุ่ม
                self.is_clicked = False

    def record_position(self):
        # บันทึกตำแหน่งปัจจุบันของเมาส์
        x, y = pyautogui.position()
        self.click_positions.append((x, y))
        self.update_label_with_clicks()

    def update_label_with_clicks(self):
        # อัปเดตข้อความใน Label ให้แสดงพิกัดของแต่ละการคลิก
        x, y = pyautogui.position()
        positions_text = "\n".join([f"การคลิกครั้งที่ {i+1}: ({px}, {py})" for i, (px, py) in enumerate(self.click_positions)])
        self.label.text = f"ตำแหน่งเมาส์: ({x}, {y})\n{positions_text}"

    def reset_positions(self, instance):
        # รีเซ็ตพิกัดที่บันทึกและตั้งค่าใหม่
        self.click_positions = []
        self.is_listening = False  # หยุดฟังการคลิกเมื่อรีเซ็ต
        self.label.text = "พิกัดถูกรีเซ็ต กด 'เริ่มการบันทึกพิกัด' เพื่อเริ่มบันทึกใหม่"
        self.start_button.disabled = True  # ปิดการใช้งานปุ่มเริ่มคลิก
        self.start_record_button.disabled = False  # เปิดการใช้งานปุ่มเริ่มการบันทึกพิกัดอีกครั้ง
        self.stop_record_button.disabled = True  # ปิดการใช้งานปุ่มยกเลิกการบันทึกพิกัด

    def start_auto_click(self, instance):
        self.label.text = "เริ่มการคลิกอัตโนมัติ..."
        time.sleep(1)  # หน่วงเวลาเล็กน้อยเพื่อให้ผู้ใช้เตรียมพร้อม

        # ทำการคลิกอัตโนมัติที่พิกัดที่บันทึกไว้
        for x, y in self.click_positions:
            pyautogui.click(x, y)
            time.sleep(1)  # ระยะห่างระหว่างการคลิกแต่ละครั้ง

        self.label.text = "การคลิกเสร็จสิ้น!"

# รันแอป
if __name__ == '__main__':
    AutoClickApp().run()
