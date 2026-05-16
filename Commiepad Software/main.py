import json
import serial
from serial.tools import list_ports
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QApplication, QColorDialog, QMainWindow, QGraphicsColorizeEffect
from PyQt6.QtCore import QResource, pyqtSignal
import time
import threading
from queue import Empty, Queue


QResource.registerResource("/Commiepad_UI/uifiles.qrc")



class MainWindow(QMainWindow):
    
    debug_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        loadUi("main.ui", self)

        
        self.scan_ports.clicked.connect(self.list_serial_ports)
        self.exit.clicked.connect(self.close_app)
        self.select_color.clicked.connect(self.UiComponents)
        self.set_color.clicked.connect(self.set_colors)
        self.ledonoff.clicked.connect(self.toggle_led)
        self.setrgbmode.clicked.connect(self.set_rgb_mode)
        self.serial_init.clicked.connect(self.Serial_init)
        self.oled_text_assign.clicked.connect(self.update_oled_text)
        self.serial_closer.clicked.connect(self.close_serial)
        self.OLED_text
        self.LED_ON = True
        self.RGB_ON_OFF_STATUS.setStyleSheet("background-color: green;")
        self.choose_rgb_mode
        self.baudrate
        self.debug_buffer = []
        self.scanned_ports = None
        self.RGB_Picker
        self.choose_port
        self.debug_browser
        self.RGB_ON_OFF_STATUS
        self.list_serial_ports()
        
        
        self.ser = serial.Serial(timeout=1)
        
        self.write_queue = Queue()
        
        self.debug_signal.connect(self.debug)
            
        
    


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
        command = ""
        if not self.ser.is_open:
            self.debug("Serial port not open!")
            return
        if self.LED_ON:
            command = {"type": "keypress", "key": "KC.RGB_TOG"}
            self.LED_ON = False
            self.RGB_ON_OFF_STATUS.setStyleSheet("background-color: red;")
            self.debug("LED turned OFF")
        else:
            command = {"type": "keypress", "key": "KC.RGB_TOG"}
            self.LED_ON = True
            self.RGB_ON_OFF_STATUS.setStyleSheet("background-color: green;")
            self.debug("LED turned ON")
        
        self.write_queue.put(command)

    def set_rgb_mode(self):
        if not self.ser.is_open:
            self.debug("Serial port not open!")
            return
        mode = self.choose_rgb_mode.currentText()
        command = ""
        if mode.lower() == "plain":
            command = {"type": "keypress", "key": "KC.RGB_MODE_PLAIN"}
            self.debug("Set RGB mode to Plain")
        elif mode.lower() == "breathing":
            command = {"type": "keypress", "key": "KC.RGB_MODE_BREATHE"}
            self.debug("Set RGB mode to Breathing")
        elif mode.lower() == "rainbow":
            command = {"type": "keypress", "key": "KC.RGB_MODE_RAINBOW"}
            self.debug("Set RGB mode to Rainbow")
        elif mode == "Breathing Rainbow":
            command = {"type": "keypress", "key": "KC.RGB_MODE_BREATHE_RAINBOW"}
            self.debug("Set RGB mode to Breathing Rainbow")
        elif mode == "Knight Rider":
            command = {"type": "keypress", "key": "KC.RGB_MODE_KNIGHT"}
            self.debug("Set RGB mode to Knight Rider")
        elif mode.lower() == "swirl":
            command = {"type": "keypress", "key": "KC.RGB_MODE_SWIRL"}
            self.debug("Set RGB mode to Swirl")
        
        self.write_queue.put(command)
    
    def update_oled_text(self):
        if not self.ser.is_open:
            self.debug("Serial port not open!")
            return
        text = self.OLED_text.toPlainText()
        self.write_queue.put({"type": "OLED", "text": text})
        self.debug(f"Updated OLED text: {text}")
    
    def list_serial_ports(self):
        ports = list_ports.comports()
        self.scanned_ports = ports
        self.choose_port.clear()
        for port in self.scanned_ports:
            self.choose_port.addItem(port.device)
            

    def set_serial(self):
        self.ser.port = self.choose_port.currentText()
        self.ser.baudrate = int(self.baudrate.currentText())
        self.debug(f"Selected port: {self.ser.port}, Baudrate: {self.ser.baudrate}")
        
    def Serial_init(self):
        self.set_serial()
        if self.ser.port is None:
            return
        if not self.ser.port:
            self.debug("No serial port selected!")
            return
        try:
            self.ser.open()
            time.sleep(1)
            self.debug(f"Opened serial port: {self.ser.port}")
            if not hasattr(self, 'serial_writer_thread') or not self.serial_writer_thread.is_alive():
                self.serial_writer_thread = threading.Thread(target=self.serial_write_worker, daemon=True)
                self.serial_writer_thread.start()
        except Exception as e:
            self.debug(f"Error opening serial port: {e}")

    def close_serial(self):
        if self.ser.is_open:
            self.ser.close()
            self.debug(f"Closed serial port: {self.ser.port}")
            self.write_queue.put(None)
            if hasattr(self, 'serial_writer_thread') and self.serial_writer_thread.is_alive():
                self.serial_writer_thread.join(timeout=2)
            
    def serial_write_worker(self):
        
        while True:
            try:
                data = self.write_queue.get(timeout=1)
                if data is None:
                    break
            
                if self.ser.is_open:
                    data = json.dumps(data) + "\n" if isinstance(data, dict) else data
                    self.ser.write(data.encode())
                    self.debug_signal.emit(f"Sent data to serial port: {data}")
                else:
                    continue
                
            except Empty:
                continue
            
            except Exception as e:
                self.debug_signal.emit(f"Error writing to serial port: {e}")

    def close_app(self):
        if self.ser.is_open:
            self.close_serial()
        self.close()
        
    def set_colors(self):
        if not self.ser.is_open:
            self.debug("Serial port not open!")
            return

        self.write_queue.put({"type": "RGB", "r": self.r, "g": self.g, "b": self.b})
        self.debug(f"Set RGB color to: R={self.r}, G={self.g}, B={self.b}")

    def debug(self, debug_text):
        self.debug_buffer.append(debug_text)
        if len(self.debug_buffer) >= 10:
            self.debug_buffer.pop(0)
        self.debug_browser.setText("\n".join(self.debug_buffer))
        
    

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()