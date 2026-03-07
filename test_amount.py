from src.fknc_adb_helper import (
    run_ocr,
    init_general_ocr,
    init_ddddocr,
    logger,
)


def main():
    reader = init_general_ocr()
    dddd = init_ddddocr()

    logger.info("loading test image...")
    with open("test/amount.png", "rb") as f:
        pic = f.read()

    result = run_ocr(reader, pic, dddd=dddd)
    assert result["造型喷雾"] == 2
    assert result["标准洒水器"] == 2
    assert result["幽灵药水"] == 3


if __name__ == "__main__":
    main()
