import os
import time
import subprocess
import random
from random import randint
from datetime import datetime, timedelta, timezone

import easyocr
import ddddocr
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from loguru import logger

SWIPE_SEEDS = True

load_dotenv()
ADB_OPTIONS = os.environ.get("ADB_OPTIONS", "")


def adb_command_prefix() -> list[str]:
    return ["adb"] + ADB_OPTIONS.split(" ")


def random_sleep(at_least_seconds: float):
    """
    睡眠至少 at_least_seconds 秒，或随机 10s~12s
    """
    time.sleep(max(at_least_seconds, random.uniform(10, 12)))


def randomize_coord(coord: int | str) -> str:
    return f"{randint(-10, 10) + coord}"


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
            adb_command_prefix()
            + [
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
        adb_command_prefix() + ["exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


def tap_screen(x: int, y: int):
    """
    模拟触控点击坐标 x, y

    随机消耗 100~180ms 完成点击
    """
    x = randomize_coord(x)
    y = randomize_coord(y)
    logger.debug(f"Clicking ({x}, {y})...")
    subprocess.call(
        adb_command_prefix()
        + [
            "shell",
            "input",
            "swipe",
            x,
            y,
            x,
            y,
            f"{randint(100, 180)}",
        ]
    )


def fetch_weather() -> bytes:
    """
    当前状态必须为仓库/商店/未查看作物。
    """

    # hard-coded for 1920x1080
    random_sleep(0)
    tap_screen(1800, 150)  # Close

    random_sleep(0)
    sleep_until_current_10min(second=45)
    tap_screen(648, 47)  # Weather info

    time.sleep(1)  # popup
    return take_screenshot()


def fetch_screenshot() -> tuple[list[bytes], bytes]:
    """
    从 adb 连接获取截图

    :param: skip_sleep 跳过等待至下个整分钟 05 秒。

    :return: 种子截图，工具截图
    """

    tap_screen(1773, 89)  # Store
    sleep_until_current_10min(second=4)

    seeds_lst = []

    utc8 = timezone(timedelta(hours=8))
    now = datetime.now(tz=utc8)
    if now.hour >= 8:
        time.sleep(1.5)  # wait for tools page to load
        seeds_lst.append(take_screenshot())
        if SWIPE_SEEDS:
            random_sleep(0)  # long sleep for operation
            swipe_store_page()
            time.sleep(1.5)
            seeds_lst.append(take_screenshot())

    random_sleep(0)  # long sleep for operation
    tap_screen(1805, 381)  # Tools
    time.sleep(1.5)  # page loading
    tools = take_screenshot()
    return seeds_lst, tools


def sleep_until_current_10min(second: int = 30):
    """
    等待到当前 10 分钟区间内的指定秒
    """

    now = datetime.now()

    # 当前 10 分钟区间起点（如 09:13 -> 09:10）
    base = now.replace(minute=(now.minute // 10) * 10, second=0, microsecond=0)

    # 本区间目标时间（如 09:10:30）
    target_time = base + timedelta(seconds=second)

    # 如果已经过了这个时间，无需处理
    if target_time <= now:
        return

    wait = (target_time - now).total_seconds()

    logger.info(f"等待 {wait:.0f} 秒")
    time.sleep(wait)


def swipe_store_page():
    """
    1920x1080
    """

    subprocess.call(
        adb_command_prefix()
        + [
            "shell",
            "input",
            "swipe",
            randomize_coord(1443),
            randomize_coord(800),
            randomize_coord(1443),
            randomize_coord(600),
            f"{randint(170, 180)}",
        ],
    )


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
