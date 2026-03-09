import time
import subprocess
from datetime import datetime, timedelta

import easyocr
import ddddocr
from loguru import logger


def fetch_screenshot(
    skip_sleep: bool = True,
) -> bytes:
    """
    从 adb 连接获取截图

    @TODO 滑动支持
    @TODO 作物识别支持
    @TODO 更多分辨率支持
    """

    # hard-coded for 1920x1080
    for x, y in [
        (960, 540),  # Cancel check crop
        (1804, 149),  # Close
        (1773, 89),  # Store
        (1805, 381),  # Tools
    ]:
        subprocess.call(["adb", "shell", "input", "tap", f"{x}", f"{y}"])
        time.sleep(1)

    if not skip_sleep:
        sleep_until_current_min_5s()

    out = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    return out


def sleep_until_current_min_5s():
    """
    等待至下个刷新时间
    """
    now = datetime.now()
    next_time = now.replace(second=5)
    wait = (next_time - now).total_seconds()

    if wait > 0:
        logger.info(f"等待 {wait:.0f} 秒 后进行截图")

        time.sleep(wait)


def sleep_until_next_10min():
    """
    等待至下个刷新时间
    """
    now = datetime.now()
    next_time = now.replace(second=0, microsecond=0) + timedelta(minutes=10)
    next_time = next_time.replace(minute=(next_time.minute // 10) * 10)

    if next_time <= now:
        next_time += timedelta(minutes=10)

    wait = (next_time - now).total_seconds()
    logger.info(f"等待 {wait:.0f} 秒，下一次运行时间 {next_time.strftime('%H:%M:%S')}")

    time.sleep(wait)


def init_ddddocr() -> ddddocr.DdddOcr:
    logger.info("加载 DDDDOcr 模型")
    d = ddddocr.DdddOcr(
        beta=True,
        use_gpu=True,
        show_ad=False,
    )
    d.set_ranges(0)
    logger.info("DDDDOcr 模型加载完成")
    return d


def init_general_ocr() -> easyocr.Reader:
    logger.info("加载 OCR 模型")
    reader = easyocr.Reader(
        ["ch_sim"],
        gpu=True,
    )
    logger.info("OCR 模型加载完成")
    return reader
