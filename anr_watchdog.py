import re
import subprocess
from datetime import datetime

PACKAGE = "com.netease.party"

# logcat 时间格式
TIME_PATTERN = re.compile(r"(\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3})")

last_anr_time: datetime | None = None


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


def kill_app():
    print("force-stop app")

    subprocess.run(
        ["adb", "shell", "am", "force-stop", PACKAGE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def restart_app():
    print("restart app")

    subprocess.run(
        [
            "adb",
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


def main():
    global last_anr_time

    print("starting ANR watchdog...")

    proc = subprocess.Popen(
        ["adb", "logcat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )

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

        print(f"ANR detected: {anr_time}")
        print(line.strip())

        kill_app()
        restart_app()


if __name__ == "__main__":
    main()
