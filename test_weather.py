from loguru import logger

from fknc_adb_helper import (
    RecognizeType,
    run_ocr,
    init_general_ocr,
)


def main():
    reader = init_general_ocr()

    logger.info("loading test image...")
    with open("test/weather.png", "rb") as f:
        pic = f.read()

    result = run_ocr(
        reader,
        screenshot=pic,
        min_confidence=0.5,
        crop_rect=(468, 103, 1084, 177),
        recognize_type=RecognizeType.WEATHER,
    )
    assert "雷雨" in result


if __name__ == "__main__":
    main()
