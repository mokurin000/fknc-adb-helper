from loguru import logger

from fknc_adb_helper import (
    RecognizeType,
    run_ocr,
    init_general_ocr,
    WEATHER_RECT,
)


def main():
    reader = init_general_ocr()

    logger.info("loading test image...")
    with open("test/weather_special.png", "rb") as f:
        pic = f.read()

    result = run_ocr(
        reader,
        screenshot=pic,
        min_confidence=0.8,
        crop_rect=WEATHER_RECT,
        recognize_type=RecognizeType.WEATHER,
    )
    assert "流星雨" in result


if __name__ == "__main__":
    main()
