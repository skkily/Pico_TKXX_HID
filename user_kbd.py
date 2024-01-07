import usb_hid
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

def test01():
    keyboard.press(Keycode.LEFT_ALT, Keycode.TAB)

def test01_r():
    keyboard.release(Keycode.LEFT_ALT, Keycode.TAB)

def test02():
    keyboard.press(Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.F3)

def test02_r():
    keyboard.release(Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.F3)

def pr_hello():
    keyboard_layout.write("hello world!")

def pr_A():
    keyboard.press(Keycode.LEFT_SHIFT, Keycode.A)

def pr_A_r():
    keyboard.release(Keycode.LEFT_SHIFT, Keycode.A)

def pr_B():
    keyboard.press(Keycode.LEFT_SHIFT, Keycode.B)

def pr_B_r():
    keyboard.release(Keycode.LEFT_SHIFT, Keycode.B)

def pr_ENT():
    keyboard.press(Keycode.ENTER)

def pr_ENT_r():
    keyboard.release(Keycode.ENTER)

def pr_BACK():
    keyboard.press(Keycode.BACKSPACE)

def pr_BACK_r():
    keyboard.release(Keycode.BACKSPACE)

keyboard_index = [
    ["alt+tab",         test01,     test01_r ],
    ["ctl+alt+F3",      test02,     test02_r ],
    ["\"hello world\"", None,       pr_hello ],
    ["KEY: ENTER",      pr_ENT,     pr_ENT_r ],
    ["KEY: A",          pr_A,       pr_A_r   ],
    ["KEY: B",          pr_B,       pr_B_r   ],
    ["KEY: Back",       pr_BACK,    pr_BACK_r],
]