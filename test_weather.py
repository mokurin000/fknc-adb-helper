from loguru import logger

from fknc_adb_helper import (
    run_ocr,
    init_general_ocr,
)


def main():
    reader = init_general_ocr()

    logger.info("loading test image...")
    with open("test/weather.png", "rb") as f:
        pic = f.read()

    run_ocr(
        reader,
        screenshot=pic,
        min_confidence=0.5,
        crop_rect=(468, 103, 1084, 177),
    )


if __name__ == "__main__":
    main()
