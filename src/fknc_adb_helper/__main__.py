import os
import sys
import time

from loguru import logger

from fknc_adb_helper import extract_info
from fknc_adb_helper.ocr import init_ddddocr, init_general_ocr
from fknc_adb_helper.utils import sleep_until_next_10min


def main():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    logger.add(
        "ocr.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        enqueue=True,
    )

    time1 = time.monotonic()
    reader = init_general_ocr()
    num_reader = init_ddddocr()
    time2 = time.monotonic()

    logger.info(f"初始化完成，耗时{time2 - time1:.2f}s")

    if "--skip-first-sleep" not in sys.argv:
        sleep_until_next_10min()

    os.makedirs("pics", exist_ok=True)

    while True:
        extract_info(
            reader=reader,
            num_reader=num_reader,
        )
        sleep_until_next_10min()


if __name__ == "__main__":
    main()
