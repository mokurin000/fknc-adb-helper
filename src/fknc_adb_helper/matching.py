import os
from threading import RLock

import cv2 as cv
from loguru import logger
from cv2.typing import MatLike

from fknc_adb_helper.utils import take_screenshot, sleep_until_current_10min

NAME_MAP = {
    "darkfog": "暗雾",
    "fog": "雾",
    "firefly": "萤光",
    "rainball": "彩虹",
    "eclipse": "日蚀",
    "sandstorm": "沙尘暴",
    "meteor-shower": "流星雨",
    "solarflare": "太阳耀斑",
    # growth speed
    "thunderstorm": "雷雨",
    "deluge": "暴雨",
    "drizzle": "细雨",
    "snow": "雪",
    # 生机
    "fair-wind": "惠风",
}

_WEATHERS = None
_WEATHERS_LOCK = RLock()


def read_gray_image(path: str | os.PathLike[str]):
    return cv.imread(path, cv.IMREAD_GRAYSCALE)


def find_weather(after_5min: bool = False) -> str | None:
    temp_path = "temp_match.png"
    for second in range(30, 51, 5):
        skipped = sleep_until_current_10min(
            second=second if not after_5min else second + 300
        )

        with open(temp_path, "wb") as f:
            f.write(take_screenshot())
        image = read_gray_image(path=temp_path)
        detected = detect_weather(image)
        if detected is not None:
            return detected

        if skipped:
            break

    return None


def detect_weather(
    image: MatLike,
    threshold: float = 0.8,
) -> str | None:
    global _WEATHERS

    with _WEATHERS_LOCK:
        if _WEATHERS is None:
            _WEATHERS = init_weathers()

    # image: 1920x1080
    image = image[24:69, 572:780]

    for weather_name, template in _WEATHERS.items():
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
        if template is None:
            logger.error(f"failed to load weather/{weather_img}")
            continue
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
