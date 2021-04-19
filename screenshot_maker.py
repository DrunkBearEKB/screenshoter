import pyautogui
import keyboard
import numpy
import cv2
import datetime
import win32clipboard
from io import BytesIO
import os
import configparser


CONFIG_FILE_NAME = 'config.ini'


def parse_config() -> configparser.ConfigParser:
    if not os.path.exists(CONFIG_FILE_NAME):
        create_default_config()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME)

    return config


def create_default_config() -> None:
    config = configparser.ConfigParser()

    config.add_section('Settings')
    config['Settings']['border_width'] = '2'
    config['Settings']['border_coef_red'] = '255'
    config['Settings']['border_coef_green'] = '255'
    config['Settings']['border_coef_blue'] = '255'
    config['Settings']['size_buffer_saving'] = '5'

    with open(CONFIG_FILE_NAME, 'w') as file:
        config.write(file)


def send_to_clipboard(clip_type, data) -> None:
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()


def make_screenshot(point1: (int, int), point2: (int, int), buf_size) -> None:
    _datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

    if not os.path.exists('screenshots'):
        os.mkdir('screenshots')

    screenshot = None
    flag_screenshot_made = False
    while not flag_screenshot_made:
        try:
            _x0 = min(point1[0], point2[0])
            _y0 = min(point1[1], point2[1])
            _x1 = max(point1[0], point2[0])
            _y1 = max(point1[1], point2[1])
            screenshot = pyautogui.screenshot(
                f'screenshots/screenshot_{_datetime}.png',
                region=(_x0, _y0, _x1 - _x0, _y1 - _y0))
            flag_screenshot_made = True
        except AttributeError:
            pass

    list_screenshots = os.listdir(f'{os.path.dirname(__file__)}\\screenshots')
    list_screenshots.sort()
    for i in range(len(list_screenshots) - buf_size):
        try:
            os.remove(f'{os.path.dirname(__file__)}\\screenshots\\'
                      f'{list_screenshots[i]}')
        except OSError:
            pass

    cv2.destroyAllWindows()

    output = BytesIO()
    screenshot.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()

    send_to_clipboard(win32clipboard.CF_DIB, data)
    screenshot.show()


def main() -> None:
    config = parse_config()
    _width = int(config['Settings']['border_width'])
    _width_half = (_width + 1) // 2 + 2
    _color = (int(config['Settings']['border_coef_blue']),
              int(config['Settings']['border_coef_green']),
              int(config['Settings']['border_coef_red']))
    _buffer_size = int(config['Settings']['size_buffer_saving'])

    while True:
        try:
            keyboard.wait('ctrl + print screen')

            screenshot = pyautogui.screenshot()

            _array_image = numpy.array(screenshot)
            image = cv2.cvtColor(_array_image, cv2.COLOR_RGB2BGR)

            cv2.namedWindow('window', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('window', cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty('window', cv2.WND_PROP_TOPMOST,
                                  cv2.WND_PROP_TOPMOST)

            _queue = []

            def mouse_evt(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    _queue.append((x, y))

                elif event == cv2.EVENT_LBUTTONUP:
                    make_screenshot(_queue[0], (x, y), _buffer_size)
                    _queue.pop(0)

                elif event == cv2.EVENT_MOUSEMOVE:
                    temp = cv2.putText(
                        cv2.cvtColor(_array_image, cv2.COLOR_RGB2BGR),
                        f' ({x}, {y})', (x, y), cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 255, 255), 1)

                    if len(_queue) != 0:
                        p1 = _queue[0]
                        p2 = (x, y)

                        if p2[0] > p1[0]:
                            if p2[1] > p1[1]:
                                p1 = (p1[0] - _width_half, p1[1] - _width_half)
                                p2 = (p2[0] + _width_half, p2[1] + _width_half)
                            else:
                                p1 = (p1[0] - _width_half, p1[1] + _width_half)
                                p2 = (p2[0] + _width_half, p2[1] - _width_half)
                        else:
                            if p2[1] > p1[1]:
                                p1 = (p1[0] + _width_half, p1[1] - _width_half)
                                p2 = (p2[0] - _width_half, p2[1] + _width_half)
                            else:
                                p1 = (p1[0] + _width_half, p1[1] + _width_half)
                                p2 = (p2[0] - _width_half, p2[1] - _width_half)

                        temp = cv2.rectangle(
                            temp, p1, p2, _color, thickness=_width)

                    cv2.imshow('window', temp)

            cv2.setMouseCallback('window', mouse_evt)
            cv2.imshow('window', image)
            cv2.waitKey(0)

        except Exception:
            pass


if __name__ == '__main__':
    main()
