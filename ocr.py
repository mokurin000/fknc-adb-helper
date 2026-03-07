import io
import os
import time
import subprocess
from datetime import datetime, timedelta

import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

from detect_item import item_exists

ADDITION_ITEMS = [
    "火盆",
    "造雪机",
    "引雷针",
    "造型喷雾",
    "农田置换卡",
]

TARGET_ITEM = [
    "流星杖",
    "月球标准洒水器",
    "月球白银洒水器",
    "月球黄金洒水器",
    "白银洒水器",
    "黄金洒水器",
]

ALIAS_MAP = {
    "月球标准洒水器": "月标",
    "月球白银洒水器": "月白",
    "月球黄金洒水器": "月金",
    "白银洒水器": "地白",
    "黄金洒水器": "地金",
}

os.makedirs("pics", exist_ok=True)
os.makedirs("test-pics", exist_ok=True)

CONFIDENCE = 0.7
font = ImageFont.truetype("msyh.ttc", 20)  # 微软雅黑

logger.add(
    "ocr.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
)


def fetch_screenshot() -> bytes:
    # hard-coded for 1920x1080
    for x, y in [
        (1804, 149),  # Close
        (1773, 89),  # Store
        (1805, 381),  # Tools
    ]:
        subprocess.call(["adb", "shell", "input", "tap", f"{x}", f"{y}"])
        time.sleep(0.5)
    out = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    return out


def init_reader() -> easyocr.Reader:
    logger.info("加载 OCR 模型")
    reader = easyocr.Reader(
        ["ch_sim"],
        gpu=True,
    )
    logger.info("OCR 模型加载完成")
    return reader


def run_ocr(
    reader: easyocr.Reader,
    pic: bytes = None,
) -> list[str]:
    found_items: list[str] = []

    try:
        screen_shot = pic or fetch_screenshot()
        scrshot_img = Image.open(io.BytesIO(screen_shot))
        scrshot_img.save("screenshot.png")

        result = reader.readtext("screenshot.png")

        ts = datetime.now().strftime("%Y-%m-%d-%H_%M")
        if pic is None:
            filename = f"pics/result_{ts}.png"
            scr_filename = f"pics/screenshot_{ts}.png"
        else:
            filename = f"test-pics/result_{ts}.png"
            scr_filename = f"test-pics/screenshot_{ts}.png"

        img = scrshot_img.copy()
        draw = ImageDraw.Draw(img)

        kept = 0

        for coords, text, confidence in result:
            if confidence < CONFIDENCE:
                continue

            pts = [(int(x), int(y)) for x, y in coords]

            draw.polygon(pts, outline="red", width=3)

            x, y = pts[0]
            draw.text(
                (x, y - 20),
                f"{text} {confidence * 100:.1f}%",
                fill="red",
                font=font,
            )

            if text in TARGET_ITEM or text in ADDITION_ITEMS:
                top_left, _, bottom_right, _ = pts
                left, top = top_left
                right, bottom = bottom_right
                region = scrshot_img.crop((left, top, right, bottom))
                if item_exists(region):
                    found_items.append(text)

            confidence: np.float64
            kept += 1

        # must have one of valuable thing
        if found_items and (set(found_items) - set(ADDITION_ITEMS)):
            found_things = "，".join(map(lambda n: ALIAS_MAP.get(n, n), found_items))
            logger.info(f"发现物品: {found_things}")
            img.save(filename)

            with open(scr_filename, "wb") as f:
                f.write(screen_shot)

    except Exception as e:
        logger.exception(f"OCR 任务失败: {e}")

    return found_items


def sleep_until_next_10min():
    now = datetime.now()
    next_time = now.replace(second=0, microsecond=0) + timedelta(minutes=10)
    next_time = next_time.replace(minute=(next_time.minute // 10) * 10, second=5)

    if next_time <= now:
        next_time += timedelta(minutes=10)

    wait = (next_time - now).total_seconds()
    logger.info(f"等待 {wait:.0f} 秒，下一次运行时间 {next_time.strftime('%H:%M:%S')}")

    time.sleep(wait)


def main():
    reader = init_reader()

    logger.info("程序启动，立即执行一次 OCR")
    run_ocr(reader)

    while True:
        sleep_until_next_10min()
        run_ocr(reader)


if __name__ == "__main__":
    main()
