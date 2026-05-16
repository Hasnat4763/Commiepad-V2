import board
import busio
import usb_cdc
from serialcommand import SerialCommand
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.extensions.RGB import RGB
from kmk.extensions.RGB.animations import AnimationModes
from kmk.extensions.encoder import EncoderHandler
from kmk.extensions.display import Display, TextEntry, ImageEntry
from kmk.extensions.display.ssd1306 import SSD1306



keyboard = KMKKeyboard()

encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)


i2c_bus = busio.I2C(board.SCL, board.SDA)

driver = SSD1306(i2c=i2c_bus, 
                  device_address=0x3C,)

keyboard.col_pins = (board.D6, board.D9, board.D3)
keyboard.row_pins = (board.D7, board.D8, board.D2)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

keyboard.keymap = [
    [KC.A, KC.B, KC.C],
    [KC.D, KC.E, KC.F],
    [KC.G, KC.H, KC.I]
]

encoder_handler.pins = (
    (board.D0, board.D1, None,),
)

encoder_handler.map = (
    (KC.VOLD, KC.VOLU, None,),
)

display = Display(
    display=driver,
    width=128,
    height=32,
    flip=False,
    flip_left=False,
    flip_right=False,
    brightness=0.5
)

display.entries = [
    TextEntry(
        text="Hello, World!", x = 0, y = 0
    )
]

rgb = RGB(pixel_pin=board.D10,
          num_pixels=8,
          rgb_order=(1,0,2),
          val_default=100,
          val_limit=100,
          hue_default=0,
          sat_default=100,
          hue_step=5,
          sat_step=5,
          val_step=5,
          animation_speed=1,
          breathe_center=1,
          bright_effect_length=3,
          animation_mode=AnimationModes.STATIC,
          reverse_animation=False,
          refresh_rate=60
          )

serial_command =  SerialCommand(keyboard=keyboard, RGB=rgb, OLED=display)
keyboard.extensions.append(serial_command)
keyboard.extensions.append(rgb)
keyboard.extensions.append(display)

if __name__ == '__main__':
    keyboard.go()