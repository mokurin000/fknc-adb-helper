from src.fknc_adb_helper import run_ocr, init_reader, logger


def main():
    reader = init_reader()

    logger.info("loading test image...")
    with open("test/moon_std.png", "rb") as f:
        pic = f.read()

    assert "月球标准洒水器" in run_ocr(reader, pic)


if __name__ == "__main__":
    main()
