import os
import time
import shutil
import subprocess
from datetime import datetime, timedelta

import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

os.makedirs("pics", exist_ok=True)

CONFIDENCE = 0.7
font = ImageFont.truetype("msyh.ttc", 20)  # 微软雅黑

logger.add(
    "ocr.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
)


def fetch_screenshot():
    logger.info("开始截图")
    with open("screenshot.png", "wb") as pic:
        subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            stdout=pic,
            check=True,
        )
    logger.info("截图完成")


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
    img_path: str = "screenshot.png",
):
    try:
        fetch_screenshot()

        logger.info("开始 OCR 识别")
        result = reader.readtext(img_path)
        logger.info(f"OCR 完成，共识别 {len(result)} 个区域")

        ts = datetime.now().strftime("%Y-%m-%d-%H_%M")
        filename = f"pics/result_{ts}.png"
        scr_filename = f"pics/screenshot_{ts}.png"

        shutil.copy2(img_path, scr_filename)

        img = Image.open(img_path)
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

            confidence: np.float64
            kept += 1

        img.save(filename)

        logger.info(f"结果保存: {filename} (置信度≥{CONFIDENCE} 的 {kept} 个)")

    except Exception:
        logger.exception("OCR 任务失败")


def sleep_until_next_10min():
    now = datetime.now()
    next_time = now.replace(second=0, microsecond=0) + timedelta(minutes=10)
    next_time = next_time.replace(minute=(next_time.minute // 10) * 10, second=10)

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
