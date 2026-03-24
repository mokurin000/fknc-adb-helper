import os
import re
import subprocess
from datetime import datetime
from threading import Thread
import time

from loguru import logger
from milky import OutgoingTextSegment, TextSegmentData
from milky.client import MilkyError, MilkyHttpError

from fknc_adb_helper.bot import BOT_CLIENT
from fknc_adb_helper.utils import adb_command_prefix, take_screenshot, utc8_time

PACKAGE = "com.netease.party"
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

# logcat 时间格式
TIME_PATTERN = re.compile(r"(\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3})")


def parse_time(line: str) -> datetime | None:
    """从 logcat 行解析时间"""
    m = TIME_PATTERN.search(line)
    if not m:
        return None

    date_part, time_part = m.groups()

    year = datetime.now().year
    return datetime.strptime(
        f"{year}-{date_part} {time_part}",
        "%Y-%m-%d %H:%M:%S.%f",
    )


def restart_app(notify: str):
    if ADMIN_ID:
        segdata = TextSegmentData(text=notify)
        outgoing_seg = OutgoingTextSegment(data=segdata)
        try:
            BOT_CLIENT.send_private_message(ADMIN_ID, [outgoing_seg])
        except MilkyHttpError | MilkyError as e:
            logger.error(f"推送失败：{e}")

    logger.info("killing process...")
    subprocess.run(
        adb_command_prefix() + ["shell", "am", "force-stop", PACKAGE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    logger.info("launching process...")
    subprocess.run(
        adb_command_prefix()
        + [
            "shell",
            "monkey",
            "-p",
            PACKAGE,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stuck_watchdog():
    logger.info("starting stuck watchdog...")

    last_screenshot = take_screenshot()
    while True:
        time.sleep(10.0)
        screenshot = take_screenshot()
        if screenshot == last_screenshot:
            restart_app(f"{utc8_time()}\n游戏画面卡死，请操作登录！")
        last_screenshot = screenshot


def anr_watchdog():
    logger.info("starting ANR watchdog...")

    # clean logcat buffer before first run
    subprocess.run(adb_command_prefix() + ["logcat", "-c"], capture_output=True)

    proc = subprocess.Popen(
        adb_command_prefix() + ["logcat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )
    last_anr_time = None

    for line in proc.stdout:
        if "WindowManager: ANR in" not in line:
            continue

        if PACKAGE not in line:
            continue

        anr_time = parse_time(line)
        if not anr_time:
            continue

        if last_anr_time == anr_time:
            continue

        last_anr_time = anr_time

        logger.info(f"detected ANR at {anr_time}")
        restart_app(f"{anr_time}\n游戏进程由于 ANR 已重启，请操作登录！")


def main():
    threads: list[Thread] = []

    for func in [
        anr_watchdog,
        stuck_watchdog,
    ]:
        thread = Thread(target=func)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
