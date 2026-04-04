from loguru import logger


from fknc_adb_helper import run_ocr, RecognizeType
from fknc_adb_helper.ocr import init_general_ocr, init_ddddocr


def main():
    reader = init_general_ocr()
    dddd = init_ddddocr()

    logger.info("loading test image...")
    with open("test/moon_std.png", "rb") as f:
        pic = f.read()

    result = run_ocr(
        reader,
        pic,
        dddd=dddd,
        recognize_type=RecognizeType.ITEM,
        save_dddd_rect=True,
    )

    assert "月球标准洒水器" in result.keys()
    assert result["月球标准洒水器"] == 2, f"found {result['月球标准洒水器']}"

    logger.info("test passed!")


if __name__ == "__main__":
    main()
