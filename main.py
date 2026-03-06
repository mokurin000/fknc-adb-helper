import subprocess

import easyocr
import numpy as np


def fetch_screenshot():
    subprocess.run(
        ["adb", "shell", "screencap", "-p", "/data/local/tmp/screenshot.png"],
    )
    subprocess.run(
        ["adb", "pull", "/data/local/tmp/screenshot.png"],
    )


def init_reader() -> easyocr.Reader:
    reader = easyocr.Reader(["ch_sim", "en"])
    return reader


fetch_screenshot()

reader = init_reader()
result = reader.readtext("screenshot.png")

for coords, text, confidence in result:
    top_left, top_right, bottom_left, bottom_right = coords
    # todo: 调用 cv2 绘制边框到识别处
    print(top_left, top_right, bottom_left, bottom_right)
    confidence: np.float64
    print(text, f"{confidence * 100:.02f}%")
