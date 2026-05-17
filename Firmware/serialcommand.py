import usb_cdc
import json
from kmk.extensions import Extension
class SerialCommand(Extension):
    def __init__(self, keyboard = None, RGB = None, OLED = None):
        self.keyboard = keyboard
        self.RGB = RGB
        self.OLED = OLED
        super().__init__()
    def process_sent_data(self, data):
        try:
            for line in data.strip().split('\n'):
                if not line:
                    continue
                command = json.loads(line)
                command_type = command.get("type")
                if command_type == "keypress":
                    key = command.get("key")
                    self.key_press(key)
                        
                elif command_type == "RGB":
                    r = command.get("r")
                    g = command.get("g")
                    b = command.get("b")
                    self.set_neopixel_color(r=r, g=g, b=b)
                    
                elif command_type == "OLED":
                    text = command.get("text", "")
                    self.set_oled_display(text)
        except Exception:
            pass
    def key_press(self, key):
        if not self.keyboard:
            return
        try:
            from kmk.keys import KC
            key = key.split('.')[-1]
            keycode = getattr(KC, key)
            self.keyboard.press(keycode)
            self.keyboard.release(keycode)
        except AttributeError:
            pass
        except Exception:
            pass    
    def set_oled_display(self, text):
        if not self.OLED or not len(self.OLED.entries) == 0:
            return
        try:
            self.OLED.entries[0].text = text
        except Exception:
            pass
    def set_neopixel_color(self, r, g, b):
        if not self.RGB:
            return
        try:
            self.RGB.set_rgb_fill(r=r, g=g, b=b)
        except Exception:
            pass
    def before_matrix_scan(self, keyboard):
        if usb_cdc.data.connected:
            try:
                if usb_cdc.data.in_waiting > 0:
                    data = usb_cdc.data.read(usb_cdc.data.in_waiting).decode('utf-8')
                    if data:
                        self.process_sent_data(data)
            except Exception:
                pass