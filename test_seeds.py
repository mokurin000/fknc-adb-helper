from loguru import logger

import fknc_adb_helper
from fknc_adb_helper import (
    run_ocr,
    init_general_ocr,
    init_ddddocr,
)

fknc_adb_helper.SAVE_SCREENSHOTS = True


def main():
    reader = init_general_ocr()
    dddd = init_ddddocr()

    logger.info("loading test image...")
    with open("test/seeds.png", "rb") as f:
        pic1 = f.read()

    result1 = run_ocr(
        reader,
        screenshot=pic1,
        dddd=dddd,
        recognize_seeds=True,
        min_confidence=0.08,
    )

    logger.info(f"scan result 1: {result1}")

    assert result1["猕猴桃种子"] == 1
    assert result1["草莓种子"] == 1

    logger.info("test passed!")


if __name__ == "__main__":
    main()
