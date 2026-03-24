import cv2 as cv
from loguru import logger

from fknc_adb_helper.matching import detect_weather


def main():
    image = cv.imread("test/weather2.png", cv.IMREAD_GRAYSCALE)
    detected = detect_weather(image)

    assert "细雨" in detected
    assert len(detected) == 1, f"{detected}"

    image = cv.imread("test/weather2_cold.png", cv.IMREAD_GRAYSCALE)
    detected = detect_weather(image)

    assert "暴雨" in detected
    assert len(detected) == 1, f"{detected}"

    logger.info("test passed!")


if __name__ == "__main__":
    main()
