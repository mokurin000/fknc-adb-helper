import time
import subprocess
from random import randint, random
from datetime import datetime, timedelta

import easyocr
import ddddocr
import numpy as np
from PIL import Image
from loguru import logger
from win10toast import ToastNotifier

NOTIFIER = ToastNotifier()
SWIPE_SEEDS = False  # danger operation


def random_sleep(at_least_seconds: float):
    """
    睡眠至少 at_least_seconds 秒，添加额外最多 2s 的延迟。
    """
    time.sleep(at_least_seconds + 2 * random())


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


def tap_screen(x: int, y: int):
    """
    模拟触控点击坐标 x, y

    随机消耗 100~180ms 完成点击
    """
    x = randomize_coord(x)
    y = randomize_coord(y)
    subprocess.call(
        [
            "adb",
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
    tap_screen(1800, 150)  # Close
    random_sleep(1)

    sleep_until_current_min(second=40)
    tap_screen(650, 40)  # Weather info
    random_sleep(1)
    return take_screenshot()


def fetch_screenshot() -> tuple[list[bytes], bytes]:
    """
    从 adb 连接获取截图

    :param: skip_sleep 跳过等待至下个整分钟 05 秒。

    :return: 种子截图，工具截图
    """

    # hard-coded for 1920x1080
    for x, y in [
        (960, 540),  # Cancel check crop
        (1804, 149),  # Close
    ]:
        tap_screen(x, y)
        random_sleep(1)

    tap_screen(1773, 89)  # Store
    sleep_until_current_min(second=4)

    seeds_lst = []

    random_sleep(1)
    seeds_lst.append(take_screenshot())
    if SWIPE_SEEDS:
        swipe_store_page()
        random_sleep(1.5)
        seeds_lst.append(take_screenshot())

    tap_screen(1805, 381)  # Tools
    random_sleep(1)
    tools = take_screenshot()
    return seeds_lst, tools


def sleep_until_current_min(second: int):
    """
    等待至下个刷新时间
    """
    now = datetime.now()
    next_time = now.replace(second=second)
    wait = (next_time - now).total_seconds()

    if wait > 10:
        try:
            NOTIFIER.show_toast(
                "蛋仔助手",
                f"请于 {wait:.1f} 秒后再操作疯狂农场客户端！",
                threaded=True,
            )
        except Exception:
            pass
    if wait > 0:
        logger.info(f"等待 {wait:.0f} 秒 后进行截图")

        random_sleep(wait)


def swipe_store_page():
    """
    1920x1080
    """

    subprocess.call(
        [
            "adb",
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

    random_sleep(wait)


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
