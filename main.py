import board
import busio
import math
import terminalio
import displayio
import digitalio
from displayio import FourWire
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_st7789 import ST7789
import usb_hid
from adafruit_hid.mouse import Mouse

class ice_button:
    def __init__(self, gp: int, name: str) -> None:
        self.btn_name = name

        self.key_pin = digitalio.DigitalInOut(gp)
        self.key_pin.direction = digitalio.Direction.INPUT
        self.key_pin.pull = digitalio.Pull.UP

        self.press_fun = None
        self.release_fun = None
        self.key_pressed = 0

    def bind(self, press_fun: function, release_fun: function) -> None:
        self.press_fun = press_fun
        self.release_fun = release_fun

    def scan(self) -> None:  
        if not self.key_pin.value:
            if self.key_pressed != 1:
                self.key_pressed = 1
                if self.press_fun is not None:
                    self.press_fun()
        if self.key_pin.value and self.key_pressed == 1:
            self.key_pressed = 0
            if self.release_fun is not None:
                self.release_fun()

class Tk_ext_board:
    def __init__(self) -> None:
        self.buttonA = ice_button(board.GP15, "A")
        self.buttonB = ice_button(board.GP17, "B")
        self.buttonX = ice_button(board.GP19, "X")
        self.buttonY = ice_button(board.GP21, "Y")
        self.buttonUP = ice_button(board.GP2, "UP")
        self.buttonDOWN = ice_button(board.GP18, "DOWN")
        self.buttonLEFT = ice_button(board.GP16, "LEFT")
        self.buttonRIGHT = ice_button(board.GP20, "RIGHT")
        self.buttonFUN = ice_button(board.GP3, "FUN")

        displayio.release_displays()

        spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
        tft_cs = board.GP9
        tft_dc = board.GP8
        tft_lite = board.GP13

        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.GP12)

        self.display = ST7789(
            display_bus,
            width=240,
            height=240,
            rowstart=80,
            rotation=270,
            backlight_pin=tft_lite,
        )

    def scan(self) -> None:
        self.buttonA.scan()
        self.buttonB.scan()
        self.buttonX.scan()
        self.buttonY.scan()
        self.buttonUP.scan()
        self.buttonDOWN.scan()
        self.buttonLEFT.scan()
        self.buttonRIGHT.scan()
        self.buttonFUN.scan()       

class top_display:
    def __init__(self, display) -> None:
        self.display = display
        self.screen = displayio.Group()
        
        self.funlayer = displayio.Group()

        self.bg_color_bitmap = displayio.Bitmap(240, 240, 1)
        self.bg_color_palette = displayio.Palette(1)
        self.bg_color_palette[0] = 0x686868
        self.bg_color = displayio.TileGrid(self.bg_color_bitmap, pixel_shader=self.bg_color_palette, x=0, y=0)
        self.funlayer.append(self.bg_color)

        self.text_area_left = label.Label(terminalio.FONT, text="KEYBOARD", color=0x0, x=2, y=234)
        self.funlayer.append(self.text_area_left)
        self.text_area_right = label.Label(terminalio.FONT, text="PAGE:01/10", color=0x0, x=178, y=234)
        self.funlayer.append(self.text_area_right)
        self.screen.append(self.funlayer)

    def todisplay(self):
        self.display.root_group = self.screen

class menu_item():
    rect_nom_color = 0xC0C0C0
    rect_press_color = 0x191970
    text_nom_color = 0x191970
    text_press_color = 0xC0C0C0

    def menu_press(self):
        self.roundrect.fill = self.rect_press_color
        self.roundrect.outline = self.rect_press_color
        self.text_area.color = self.text_press_color
        if self.area_press_function is not None:
            self.area_press_function()

    def menu_release(self):
        self.roundrect.fill = self.rect_nom_color
        self.roundrect.outline = self.rect_nom_color
        self.text_area.color = self.text_nom_color
        if self.area_release_function is not None:
            self.area_release_function()

    def bind_btn(self, btn:ice_button):
        btn.bind(self.menu_press, self.menu_release)

    def set_text(self, text: str):
        self.text_area.text = text[:15]+" "*(15 -len(text[:15])) + " >"

    def __init__(self, menu_area: displayio.Group, x, y) -> None:
        self.menu_area = menu_area
        self.roundrect = RoundRect(x, y, 230, 50, 10, fill=self.rect_nom_color, outline=self.rect_nom_color, stroke=3)
        self.menu_area.append(self.roundrect)
        self.text_area = label.Label(terminalio.FONT, text="Hello Menu", color=self.text_nom_color, x=x+15, y=y+25, scale=2)
        self.menu_area.append(self.text_area)
        self.area_release_function = None
        self.area_press_function = None

class four_menu(top_display):
    def __menu_update(self, page):
        if page == 0:
            page = 1
        pages = math.ceil(len(self.menu_index)/4)
        if pages < page:
            return
        
        index = page - 1
        times = 0
        for num,item in enumerate(self.menu_index[index*4:]):
            self.items[num].set_text(item[0])
            self.items[num].area_press_function = item[1]
            self.items[num].area_release_function = item[2]
            times = num
            if num == 3:
                break

        if times != 3:
            for i in range(times + 1, 4):
                self.items[i].set_text("")
                self.items[i].area_press_function = None
                self.items[i].area_release_function = None

        self.page = page
        self.text_area_right.text = "PAGE "+str("{:02d}".format(page))+"/"+str("{:02d}".format(pages))

    def page_refresh(self, page, menu_index):
        self.menu_index = menu_index
        self.__menu_update(page)

    def bind_four_btns(self, btn1:ice_button, btn2:ice_button, btn3:ice_button, btn4:ice_button):
        btn1.bind(self.items[0].menu_press, self.items[0].menu_release)
        btn2.bind(self.items[1].menu_press, self.items[1].menu_release)
        btn3.bind(self.items[2].menu_press, self.items[2].menu_release)
        btn4.bind(self.items[3].menu_press, self.items[3].menu_release)

    def __init__(self, display) -> None:
        super().__init__(display)
        self.four_menu = displayio.Group()

        self.items = []
        self.items.append(menu_item(self.four_menu, 5, 5))
        self.items.append(menu_item(self.four_menu, 5, 62))
        self.items.append(menu_item(self.four_menu, 5, 119))
        self.items.append(menu_item(self.four_menu, 5, 176))

        self.screen.append(self.four_menu)

        self.page = 1

class keyboard_mode:
    def __init__(self, keyboard_index, four_menu: four_menu) -> None:
        self.keyboard_index = keyboard_index
        self.four_menu = four_menu

    def __next_page(self):
        self.four_menu.page_refresh(self.four_menu.page + 1, self.keyboard_index)

    def __prev_page(self):
        self.four_menu.page_refresh(self.four_menu.page - 1, self.keyboard_index)

    def bind_direct_btns(self, btn1:ice_button, btn2:ice_button, btn3:ice_button, btn4:ice_button):
        self.btn1 = btn1
        self.btn2 = btn2
        self.btn3 = btn3
        self.btn4 = btn4

    def enable(self):
        self.four_menu.text_area_left.text = "KEYBOARD"
        self.four_menu.page_refresh(self.four_menu.page, self.keyboard_index)
        self.btn1.bind(None, self.__prev_page)
        self.btn2.bind(None, self.__next_page)
        self.btn3.bind(None, self.__prev_page)
        self.btn4.bind(None, self.__next_page)

class mouse_mode:
    def __a(self):
        if self.speed == 6:
            self.speed = 2
        elif self.speed == 2:
            self.speed = 3
        elif self.speed == 3:
            self.speed = 4
        elif self.speed == 4:
            self.speed = 6
        self.function[0][0] = "SPEED: " + str(self.speed)
        four_menu.page_refresh(1, self.function)

    def __y(self):
        self.mouse.press(Mouse.LEFT_BUTTON)

    def __y_r(self):
        self.mouse.release(Mouse.LEFT_BUTTON)

    def __x(self):
        self.mouse.press(Mouse.RIGHT_BUTTON)

    def __x_r(self):
        self.mouse.release(Mouse.RIGHT_BUTTON)
        

    def __init__(self, four_menu) -> None:
        self.mouse = Mouse(usb_hid.devices)
        self.speed = 3
        self.four_menu = four_menu
        self.function = [
            ["SPEED: " + str(self.speed),self.__a,None],
            ["",None,None],
            ["R CLICK",self.__x,self.__x_r],
            ["L CLICK",self.__y,self.__y_r],
        ]

        self.mouse = Mouse(usb_hid.devices)

    def __x_a(self):
        self.mouse.move(x=self.speed)
        self.btn4.key_pressed = 0

    def __x_b(self):
        self.mouse.move(x=-self.speed)
        self.btn3.key_pressed = 0

    def __y_a(self):
        self.mouse.move(y=self.speed)
        self.btn2.key_pressed = 0

    def __y_b(self):
        self.mouse.move(y=-self.speed)
        self.btn1.key_pressed = 0

    def bind_direct_btns(self, btn1:ice_button, btn2:ice_button, btn3:ice_button, btn4:ice_button):
        self.btn1 = btn1
        self.btn2 = btn2
        self.btn3 = btn3
        self.btn4 = btn4

    def enable(self):
        self.four_menu.text_area_left.text = "MOUSE"
        self.four_menu.page_refresh(1, self.function)
        self.btn1.bind(self.__y_b, None)   
        self.btn2.bind(self.__y_a, None)
        self.btn3.bind(self.__x_b, None)
        self.btn4.bind(self.__x_a, None)

Tk_ext_board = Tk_ext_board()
four_menu = four_menu(Tk_ext_board.display)
four_menu.bind_four_btns(Tk_ext_board.buttonA, Tk_ext_board.buttonB, Tk_ext_board.buttonX, Tk_ext_board.buttonY)

mouse_mode = mouse_mode(four_menu)
mouse_mode.bind_direct_btns(Tk_ext_board.buttonLEFT, Tk_ext_board.buttonRIGHT, Tk_ext_board.buttonDOWN, Tk_ext_board.buttonUP)

import user_kbd
keyboard_mode = keyboard_mode(user_kbd.keyboard_index, four_menu)
keyboard_mode.bind_direct_btns(Tk_ext_board.buttonUP, Tk_ext_board.buttonDOWN, Tk_ext_board.buttonLEFT, Tk_ext_board.buttonRIGHT)

BOARD_MODE = True
def fun_switch():
    global BOARD_MODE
    if BOARD_MODE is True:
        keyboard_mode.enable()
        BOARD_MODE = False
    else:
        mouse_mode.enable()
        BOARD_MODE = True

Tk_ext_board.buttonFUN.bind(None, fun_switch)
fun_switch()

four_menu.todisplay()
while True:
    Tk_ext_board.scan()

