import pyautogui
import keyboard
import numpy
import cv2
import datetime
import win32clipboard
from io import BytesIO
import os


def send_to_clipboard(clip_type, data) -> None:
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()


def make_screenshot(point1: (int, int), point2: (int, int), ) -> None:
    _datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

    if not os.path.exists('screenshots'):
        os.mkdir('screenshots')

    screenshot = pyautogui.screenshot(
        f'screenshots/screenshot_{_datetime}.png',
        region=(point1[0],
                point1[1],
                point2[0] - point1[0],
                point2[1] - point1[1]))
    print(f'Saved to file: `{os.path.dirname(__file__)}\\screenshots\\'
          f'screenshot_{_datetime}.png`')

    list_screenshots = os.listdir(f'{os.path.dirname(__file__)}\\screenshots')
    list_screenshots.sort()
    for i in range(len(list_screenshots) - 5):
        try:
            os.remove(f'{os.path.dirname(__file__)}\\screenshots\\'
                      f'{list_screenshots[i]}')
            print(f'Removed file: `{os.path.dirname(__file__)}\\screenshots\\'
                  f'{list_screenshots[i]}`')
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
                    make_screenshot(_queue[0], (x, y))
                    _queue.pop(0)
                elif event == cv2.EVENT_MOUSEMOVE:
                    if len(_queue) != 0:
                        p1 = _queue[0]
                        p2 = (x, y)

                        if p2[0] > p1[0]:
                            if p2[1] > p1[1]:
                                p1 = (p1[0] - 1, p1[1] - 1)
                                p2 = (p2[0] + 1, p2[1] + 1)
                            else:
                                p1 = (p1[0] - 1, p1[1] + 1)
                                p2 = (p2[0] + 1, p2[1] - 1)
                        else:
                            if p2[1] > p1[1]:
                                p1 = (p1[0] + 1, p1[1] - 1)
                                p2 = (p2[0] - 1, p2[1] + 1)
                            else:
                                p1 = (p1[0] + 1, p1[1] + 1)
                                p2 = (p2[0] - 1, p2[1] - 1)

                        cv2.imshow('window', cv2.rectangle(
                            cv2.cvtColor(_array_image, cv2.COLOR_RGB2BGR),
                            p1, p2, (255, 255, 255),
                            thickness=2))

            cv2.setMouseCallback('window', mouse_evt)
            cv2.imshow('window', image)
            cv2.waitKey(0)

        except Exception:
            pass


if __name__ == '__main__':
    main()
