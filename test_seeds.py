from loguru import logger

from fknc_adb_helper import (
    RecognizeType,
    run_ocr,
    init_general_ocr,
    init_ddddocr,
)


def main():
    reader = init_general_ocr()
    dddd = init_ddddocr()

    logger.info("loading test image...")
    with open("test/seeds.png", "rb") as f:
        pic = f.read()

    result = run_ocr(
        reader,
        screenshot=pic,
        dddd=dddd,
        min_confidence=0.08,
        recognize_type=RecognizeType.SEED,
    )

    logger.info(f"scan result: {result}")

    assert result["草莓种子"] == 1

    logger.info("test passed!")


if __name__ == "__main__":
    main()
