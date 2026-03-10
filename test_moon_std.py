from loguru import logger

from fknc_adb_helper import run_ocr, init_general_ocr


def main():
    reader = init_general_ocr()

    logger.info("loading test image...")
    with open("test/moon_std.png", "rb") as f:
        pic = f.read()

    assert "月球标准洒水器" in run_ocr(reader, pic).keys()
    logger.info("test passed!")


if __name__ == "__main__":
    main()
