import time
import threading
from pynput import mouse
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
from win32api import GetSystemMetrics
from itertools import cycle
import random
import sys

print(f'screen width = {GetSystemMetrics(0)}, screen hieght = {GetSystemMetrics(1)}')

position_selection_counter = 0
button = Button.right
start_stop_key = KeyCode(char='[')
exit_key = KeyCode(char=']')
mouse_positions = []

if len(sys.argv) == 3:
    delay = int(sys.argv[1]) if int(sys.argv[1]) > 0 else 5 
    position_selection_amount = int(sys.argv[2]) if int(sys.argv[2]) > 0 else exit(-1)    
else:
    print('provide delay and amount of positions in this order')
    exit(-1)

def mouse_positions_collector(x, y, button_clicked, pressed):
    global position_selection_counter, position_selection_amount, mouse_positions
    if button_clicked is Button.left and pressed is False:
        mouse_positions.append((x,y))
        position_selection_counter += 1
        print(f'mouse position ({x}, {y}) is added. current positions counter = {position_selection_counter}')
        if position_selection_amount == position_selection_counter:
            listener.stop()
    else:
        print('click with left mouse button to select positions.')

# https://github.com/moses-palmer/pynput/issues/32 -> reason why pressing on terminal window causes mouse to freeze/ be laggy
with mouse.Listener(on_click=mouse_positions_collector) as listener:
    print('provide mouse positions to choose from by left clicking on screen')
    listener.join()
    print(f'mouse positions = {mouse_positions}')

# make mouse positions list cycled to cycle through each element
mouse_positions = cycle(mouse_positions)

print(f'press {start_stop_key.char} to start/stop the script. press {exit_key} to exit script. Waiting for orders...')

class ClickMouse(threading.Thread):
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True
        self.screen_width = GetSystemMetrics(0)
        self.screen_height = GetSystemMetrics(1)

    def get_random_mouse_position(self):
        rnd_int_width = random.randint(0, self.screen_width)
        rnd_int_height = random.randint(0, self.screen_height)
        return (rnd_int_width, rnd_int_height)

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                print('The current pointer position is {0}'.format(mouse.position))
                #rnd_int = random.randint(0, 2)
                #if rnd_int > 1:
                #    mouse.position = self.get_random_mouse_position()
                #else:
                #    mouse.position = next(mouse_positions)
                mouse.position = next(mouse_positions)
                mouse.click(self.button)
                time.sleep(self.delay)
            time.sleep(0.1)

mouse = Controller()
click_thread = ClickMouse(delay, button)
click_thread.start()


def on_press(key):
    if key == start_stop_key:
        if click_thread.running:
            click_thread.stop_clicking()
            print('Script stopped.')
        else:
            click_thread.start_clicking()
            print('Script running.')
    elif key == exit_key:
        click_thread.exit()
        listener.stop()
        print('Script exited.')


with Listener(on_press=on_press) as listener:
    listener.join()