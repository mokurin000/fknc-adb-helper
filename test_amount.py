from loguru import logger

from fknc_adb_helper import (
    run_ocr,
    init_general_ocr,
    init_ddddocr,
)


def main():
    reader = init_general_ocr()
    dddd = init_ddddocr()

    logger.info("loading test image...")
    with open("test/amount.png", "rb") as f:
        pic = f.read()

    result = run_ocr(reader, pic, dddd=dddd)
    assert result["月球白银洒水器"] == 1
    assert result["标准洒水器"] == 2
    logger.info("test passed!")


if __name__ == "__main__":
    main()
