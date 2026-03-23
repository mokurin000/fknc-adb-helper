from os import listdir

import cv2 as cv
from loguru import logger
from cv2.typing import MatLike

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


def detect_weather(threshold: float = 0.8):
    pass


def init_weathers() -> dict[str, MatLike]:
    weather_map = {}
    weather_icons = listdir("weather/")
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
