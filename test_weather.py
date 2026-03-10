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
    with open("test/weather_eclipse.png", "rb") as f:
        pic2 = f.read()

    result = run_ocr(
        reader,
        screenshot=pic,
        min_confidence=0.5,
        crop_rect=WEATHER_RECT,
        recognize_type=RecognizeType.WEATHER,
    )
    assert "流星雨" in result

    result2 = run_ocr(
        reader,
        screenshot=pic2,
        min_confidence=0.5,
        crop_rect=WEATHER_RECT,
        recognize_type=RecognizeType.WEATHER,
    )
    assert "日蚀" in result2


if __name__ == "__main__":
    main()
