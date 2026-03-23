from loguru import logger

from fknc_adb_helper import run_ocr
from fknc_adb_helper.ocr import (
    init_general_ocr,
    init_ddddocr,
)


def main():
    reader = init_general_ocr()
    dddd = init_ddddocr()

    logger.info("loading test image...")
    with open("test/brazier.png", "rb") as f:
        pic = f.read()

    result = run_ocr(reader, pic, dddd=dddd, save_dddd_rect=True)
    assert result["火盆"] == 1
    logger.info("test passed!")


if __name__ == "__main__":
    main()
