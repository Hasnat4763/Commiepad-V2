import json
import serial
from serial.tools import list_ports
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QApplication, QColorDialog, QMainWindow, QGraphicsColorizeEffect
from PyQt6.QtCore import QResource
import time
import threading


QResource.registerResource("/Commiepad_UI/uifiles.qrc")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main.ui", self)

        self.ser = serial.Serial()
        self.scan_ports.clicked.connect(self.list_serial_ports)
        self.select_port.clicked.connect(self.set_serial)
        self.exit.clicked.connect(self.close_app)
        self.select_color.clicked.connect(self.UiComponents)
        self.set_color.clicked.connect(self.set_colors)
        self.ledonoff.clicked.connect(self.toggle_led)
        self.setrgbmode.clicked.connect(self.set_rgb_mode)
        self.serial_init.clicked.connect(self.Serial_init)
        self.oled_text_assign.clicked.connect(self.update_oled_text)
        self.OLED_text
        self.LED_ON = True
        self.RGB_ON_OFF_STATUS.setStyleSheet("background-color: green;")
        self.choose_rgb_mode
        self.baudrate
        self.debug_buffer = []
        self.RGB_Picker
        self.choose_port
        self.debug_browser
        self.RGB_ON_OFF_STATUS
        self.list_serial_ports()
            
        self.serial_reader = threading.Thread(target=self.serial_read, daemon=True)
        self.serial_reader.start()
    


    def UiComponents(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.RGB_Picker.setStyleSheet(f"background-color: {color.name()};")
            r, g, b, _ = color.getRgb()
            self.r = r
            self.g = g
            self.b = b
            self.set_colors()
    
    def toggle_led(self):
        if not self.ser.is_open:
            return
        if self.LED_ON:
            self.serial_write({"type": "keypress", "key": "KC.RGB_TOG"})
            self.LED_ON = False
            self.RGB_ON_OFF_STATUS.setStyleSheet("background-color: red;")
        else:
            self.serial_write({"type": "keypress", "key": "KC.RGB_TOG"})
            self.LED_ON = True
            self.RGB_ON_OFF_STATUS.setStyleSheet("background-color: green;")

    def set_rgb_mode(self):
        mode = self.choose_rgb_mode.currentText()
        if mode.lower() == "plain":
            self.serial_write({"type": "keypress", "key": "KC.RGB_MODE_PLAIN"})
            self.debug("Set RGB mode to Plain")
        elif mode.lower() == "breathing":
            self.serial_write({"type": "keypress", "key": "KC.RGB_MODE_BREATHE"})
            self.debug("Set RGB mode to Breathing")
        elif mode.lower() == "rainbow":
            self.serial_write({"type": "keypress", "key": "KC.RGB_MODE_RAINBOW"})
            self.debug("Set RGB mode to Rainbow")
        elif mode == "Breathing Rainbow":
            self.serial_write({"type": "keypress", "key": "KC.RGB_MODE_BREATHE_RAINBOW"})
            self.debug("Set RGB mode to Breathing Rainbow")
        elif mode == "Knight Rider":
            self.serial_write({"type": "keypress", "key": "KC.RGB_MODE_KNIGHT"})
            self.debug("Set RGB mode to Knight Rider")
        elif mode.lower() == "swirl":
            self.serial_write({"type": "keypress", "key": "KC.RGB_MODE_SWIRL"})
            self.debug("Set RGB mode to Swirl")
    
    def update_oled_text(self):
        text = self.OLED_text.toPlainText()
        self.serial_write({"type": "OLED", "text": text})
        self.debug(f"Updated OLED text: {text}")
    
    def list_serial_ports(self):
        ports = list_ports.comports()
        for port in ports:
            if self.choose_port.findText(port.device) == -1:
                self.choose_port.addItem(port.device)

    def set_serial(self):
        self.ser.port = self.choose_port.currentText()
        self.ser.baudrate = int(self.baudrate.currentText())
        self.debug(f"Selected port: {self.ser.port}, Baudrate: {self.ser.baudrate}")
        
    def Serial_init(self):
        if self.ser.port is None:
            return
        if not self.ser.port:
            self.debug("No serial port selected!")
            return
        try:
            self.ser.open()
            time.sleep(1)
            self.debug(f"Opened serial port: {self.ser.port}")
        except Exception as e:
            self.debug(f"Error opening serial port: {e}")

    def close_serial(self):
        if self.ser.is_open:
            self.ser.close()
            self.debug(f"Closed serial port: {self.ser.port}")
            
    def serial_write(self, data):
        if self.ser.is_open:
            data = json.dumps(data) + "\n" if isinstance(data, dict) else data
            self.ser.write(data.encode())
            self.debug(f"Sent data: {data.strip()} to {self.ser.port}")
            
            
    def serial_read(self):
        if self.ser.is_open:
            self.debug_buffer.append(self.ser.read_all().decode())

    def close_app(self):
        if self.ser.is_open:
            self.ser.close()
        self.close()
        
    def set_colors(self):
        if not self.ser.is_open:
            self.debug("Serial port not open!")
            return

        self.serial_write({"type": "RGB", "r": self.r, "g": self.g, "b": self.b})

    def debug(self, debug_text):
        self.debug_buffer.append(debug_text)
        self.debug_browser.setText("\n".join(self.debug_buffer))
        if len(self.debug_buffer) >= 10:
            self.debug_buffer.pop(0)
    

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()