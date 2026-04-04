import os
import time
import subprocess
import random
from random import randint
from datetime import datetime, timedelta, timezone


from dotenv import load_dotenv
from loguru import logger

load_dotenv()
ADB_OPTIONS = os.environ.get("ADB_OPTIONS", "")
# Weather icon left, top, right, bottom
WEATHER_RECT = (607, 24, 652, 69)


def adb_command_prefix() -> list[str]:
    return ["adb"] + ADB_OPTIONS.split(" ")


def random_sleep(reason: str = ""):
    """
    睡眠随机 12s~15s
    """
    seconds = random.uniform(12, 15)
    logger.debug(f"Sleeping {seconds:.2f}s..." + f" {reason}" if reason else "")
    time.sleep(seconds)


def randomize_coord(coord: int | str) -> str:
    return f"{randint(-10, 10) + coord}"


def is_eggy_party() -> bool:
    return (
        subprocess.call(
            adb_command_prefix()
            + [
                "shell",
                "dumpsys activity top | grep 'ACTIVITY com.netease.party/.Client'",
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
        adb_command_prefix() + ["exec-out", "sh", "-c", "screencap -p 2> /dev/null"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


def utc8_time() -> datetime:
    utc8 = timezone(timedelta(hours=8))
    now = datetime.now(tz=utc8)
    return now


def fetch_screenshot() -> tuple[list[bytes], bytes]:
    """
    从 adb 连接获取截图

    :return: 种子截图，工具截图
    """

    sleep_until_current_10min(second=15)
    tools = take_screenshot()
    return [], tools


def sleep_until_current_10min(second: int = 30) -> bool:
    """
    等待到当前 10 分钟区间内的指定秒

    返回是否被跳过
    """

    now = datetime.now()

    # 当前 10 分钟区间起点（如 09:13 -> 09:10）
    base = now.replace(minute=(now.minute // 10) * 10, second=0, microsecond=0)

    # 本区间目标时间（如 09:10:30）
    target_time = base + timedelta(seconds=second)

    # 如果已经过了这个时间，无需处理
    if target_time <= now:
        return True

    wait = (target_time - now).total_seconds()

    logger.debug(f"等待 {wait:.0f}s...")
    time.sleep(wait)
    return False


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
