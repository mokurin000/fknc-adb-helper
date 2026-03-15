import time
import subprocess
from datetime import datetime, timedelta

import easyocr
import ddddocr
import numpy as np
from PIL import Image
from loguru import logger


def common_ocr(
    reader: easyocr.Reader,
    pic: bytes | Image.Image,
) -> list[
    tuple[
        list[tuple[int, int]],
        str,
        np.float64,
    ]
]:
    if isinstance(pic, Image.Image):
        pic.save("temp.png")
    elif isinstance(pic, bytes):
        with open("temp.png", "wb") as f:
            f.write(pic)
    else:
        raise TypeError()

    result = reader.readtext("temp.png")
    return result


def is_eggy_party() -> bool:
    return (
        subprocess.call(
            [
                "adb",
                "shell",
                "dumpsys activity | grep -E 'mCurrentFocus' | grep 'com.netease.party/com.netease.party.Client'",
            ],
            stdout=subprocess.PIPE,
        )
        == 0
    )


def take_screenshot() -> bytes:
    """
    获取当前屏幕截图，返回PNG字节
    """
    return subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


def fetch_screenshot() -> tuple[list[bytes], bytes]:
    """
    从 adb 连接获取截图

    :param: skip_sleep 跳过等待至下个整分钟 05 秒。

    :return: 种子截图，工具截图
    """

    sleep_until_current_min(second=5)
    tools = take_screenshot()
    return [], tools


def sleep_until_current_min(second: int):
    """
    等待至下个刷新时间
    """
    now = datetime.now()
    next_time = now.replace(second=second)
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
