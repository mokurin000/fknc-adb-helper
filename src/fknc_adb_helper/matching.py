import os
from threading import RLock

import cv2 as cv
from loguru import logger
from cv2.typing import MatLike

from fknc_adb_helper.utils import take_screenshot, sleep_until_current_10min

NAME_MAP = {
    "darkfog": "暗雾",
    "eclipse": "日蚀",
    "firefly": "萤光",
    "meteor-shower": "流星雨",
    "rainball": "彩虹",
    "sandstorm": "沙尘暴",
    "solarflare": "太阳耀斑",
    "thunderstorm": "雷雨",
}

_WEATHERS = None
_WEATHERS_LOCK = RLock()


def read_gray_image(path: str | os.PathLike[str]):
    return cv.imread(path, cv.IMREAD_GRAYSCALE)


def find_weather() -> str | None:
    temp_path = "temp_match.png"
    for second in range(20, 46, 5):
        sleep_until_current_10min(second=second)
        with open(temp_path, "wb") as f:
            f.write(take_screenshot())
        image = read_gray_image(path=temp_path)
        detected = detect_weather(image)
        if detected is not None:
            return detected
    return None


def detect_weather(
    image: MatLike,
    threshold: float = 0.8,
) -> str | None:
    global _WEATHERS

    with _WEATHERS_LOCK:
        if _WEATHERS is None:
            _WEATHERS = init_weathers()

    for weather_name, template in _WEATHERS:
        if match_object(
            image=image,
            template=template,
            threshold=threshold,
        ):
            return weather_name

    return None


def init_weathers() -> dict[str, MatLike]:
    weather_map = {}
    weather_icons = os.listdir("weather/")
    for weather_img in weather_icons:
        weather_name = weather_img.removesuffix(".png")

        if weather_name not in NAME_MAP:
            logger.warning(f"unknown weather: {weather_name}")
            continue
        weather_name = NAME_MAP[weather_name]

        template = cv.imread(f"weather/{weather_img}", cv.IMREAD_GRAYSCALE)
        weather_map[weather_name] = template

    return weather_map


def match_object(
    image: MatLike,
    template: MatLike,
    threshold=0.8,
):

    res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)

    if max_val >= threshold:
        h, w = template.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        image_color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        cv.rectangle(image_color, top_left, bottom_right, (0, 255, 0), 2)

        return True
    else:
        return False
