import os

import cv2 as cv
from loguru import logger

from fknc_adb_helper.matching import match_object


def test_match(
    weather: str,
    test_weather: str = None,
    threshold=0.8,
):
    template = cv.imread(f"weather/{weather}.png", cv.IMREAD_GRAYSCALE)
    image = cv.imread(
        f"weather-test/{test_weather or weather}.png", cv.IMREAD_GRAYSCALE
    )

    if template is None or image is None:
        raise OSError("Failed to load images")

    return match_object(
        image=image,
        template=template,
        threshold=threshold,
    )


if __name__ == "__main__":
    test_pics = [w.removesuffix(".png") for w in os.listdir("weather-test")]

    # matching test
    for weather in test_pics:
        try:
            assert test_match(weather)
        except AssertionError:
            logger.error(f"{weather} matching failed!")
        else:
            logger.info(f"{weather} matching passed!")

    # not matching test
    for weather in test_pics:
        others = set(test_pics)
        others.remove(weather)
        for other in others:
            try:
                assert not test_match(weather, test_weather=other)
            except AssertionError:
                logger.error(f"{weather} in {other} not matching failed!")
            else:
                logger.info(f"{weather} in {other} not matching passed!")
