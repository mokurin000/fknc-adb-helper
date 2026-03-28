import os
from datetime import datetime
from threading import RLock

import cv2 as cv
from loguru import logger
from cv2.typing import MatLike

from fknc_adb_helper.utils import take_screenshot, sleep_until_current_10min
from fknc_adb_helper.config import SAVE_RESULT

NAME_MAP = {
    "darkfog": "暗雾",
    "fog": "雾",
    "firefly": "荧光",
    "rainball": "彩虹",
    "eclipse": "日蚀",
    "sandstorm": "沙尘暴",
    "meteor-shower": "流星雨",
    "solarflare": "太阳耀斑",
    "meteorite": "陨石雨",
    "neon": "霓虹",
    # growth speed
    "thunderstorm": "雷雨",
    "deluge": "暴雨",
    "drizzle": "细雨",
    "snow": "雪",
    # common but useful mutations
    "fair-wind": "惠风",
}

_WEATHERS: dict[str, tuple[MatLike, MatLike | None]] | None = None
_WEATHERS_LOCK = RLock()


def init_weathers() -> dict[str, tuple[MatLike, MatLike | None]]:
    """Load weather icons with alpha mask to ignore transparent regions"""
    weather_map: dict[str, tuple[MatLike, MatLike | None]] = {}
    weather_icons = os.listdir("weather/")

    for weather_img in weather_icons:
        weather_name = weather_img.removesuffix(".png")
        if weather_name not in NAME_MAP:
            logger.warning(f"unknown weather: {weather_name}")
            continue

        full_path = f"weather/{weather_img}"
        # Load image with alpha channel
        icon = cv.imread(full_path, cv.IMREAD_UNCHANGED)

        if icon is None:
            logger.error(f"failed to load {full_path}")
            continue

        # Handle images with alpha channel
        if len(icon.shape) == 3 and icon.shape[2] == 4:  # RGBA
            bgr = icon[:, :, :3]
            alpha = icon[:, :, 3]
            template = cv.cvtColor(bgr, cv.COLOR_BGR2GRAY)
            # Create mask from alpha (ignore fully transparent areas)
            _, mask = cv.threshold(alpha, 20, 255, cv.THRESH_BINARY)
        else:
            # No alpha channel
            template = (
                cv.cvtColor(icon, cv.COLOR_BGR2GRAY) if len(icon.shape) == 3 else icon
            )
            logger.warning(f"missing alpha info of {full_path}")
            mask = None

        chinese_name = NAME_MAP[weather_name]
        weather_map[chinese_name] = (template, mask)

    if not weather_map:
        logger.warning("No weather templates loaded!")

    return weather_map


def match_object(
    image: MatLike,
    template: MatLike,
    mask: MatLike | None = None,
    threshold: float = 0.9,
) -> bool:
    """Template matching that ignores transparent regions using mask"""
    if mask is None:
        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    else:
        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED, mask=mask)

    _, max_val, _, _ = cv.minMaxLoc(res)
    return max_val >= threshold


def detect_weather(image: MatLike, threshold: float = 0.85) -> list[str]:
    """Detect weather from screenshot using templates with transparency support"""
    global _WEATHERS
    with _WEATHERS_LOCK:
        if _WEATHERS is None:
            _WEATHERS = init_weathers()

    # ROI region crop
    weather_region = image[24:69, 572:780]

    if SAVE_RESULT:
        ts = datetime.now().strftime("%Y-%m-%d-%H_%M")
        filename = f"pics/{ts}-weather-result.png"
        cv.imwrite(filename, img=weather_region)

    # Convert to grayscale for matching
    if len(weather_region.shape) == 3:
        gray_image = cv.cvtColor(weather_region, cv.COLOR_BGR2GRAY)
    else:
        gray_image = weather_region

    detected = []
    for weather_name, (template, mask) in _WEATHERS.items():
        if match_object(
            image=gray_image,
            template=template,
            mask=mask,
            threshold=threshold,
        ):
            detected.append(weather_name)

    return detected


def find_weather(after_5min: bool = False) -> list[str]:
    """Try to detect weather multiple times around the 10-minute mark"""
    temp_path = "temp_match.png"

    for second in range(30, 61, 5):
        skipped = sleep_until_current_10min(
            second=second if not after_5min else second + 300
        )

        # Take screenshot
        screenshot_data = take_screenshot()
        with open(temp_path, "wb") as f:
            f.write(screenshot_data)

        image = read_gray_image(path=temp_path)  # Note: this still returns grayscale
        detected = detect_weather(image, threshold=0.9)

        if detected:
            logger.info(f"Weather detected: {detected}")
            return detected

        if skipped:
            break

    return []


def read_gray_image(path: str | os.PathLike[str]):
    return cv.imread(path, cv.IMREAD_GRAYSCALE)
