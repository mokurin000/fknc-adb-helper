import io
import os
import time
from datetime import datetime, timedelta

import ddddocr
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

from fknc_adb_helper.adb_utils import fetch_screenshot
from fknc_adb_helper.detect_item import item_exists

SAVE_SCREENSHOTS = False

ITEM_BG_WIDTH = 165
ITEM_PRICE_WIDTH = 50
ITEM_HEIGHT = 40

TARGET_ITEMS = [
    "月球黄金洒水器",
    "黄金洒水器",
    "流星杖",
    "月球白银洒水器",
    "白银洒水器",
    "月球标准洒水器",
]

ADDITION_ITEMS = [
    "农田置换卡",
    "幽灵药水",
    "引雷针",
    "火盆",
    "造雪机",
    "唤醒机",
    "造型喷雾",
    "标准洒水器",
]


ALIAS_MAP = {
    "月球简易洒水器": "月简",
    "月球标准洒水器": "月标",
    "月球白银洒水器": "月白",
    "月球黄金洒水器": "月金",
    "简易洒水器": "地简",
    "标准洒水器": "地标",
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


def run_ocr(
    reader: easyocr.Reader,
    pic: bytes = None,
    dddd: ddddocr.DdddOcr = None,
) -> dict[str, int]:
    found_items: dict[str] = {}

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

            top_left, _, bottom_right, _ = pts
            left, top = top_left
            right, bottom = bottom_right

            if text in TARGET_ITEMS or text in ADDITION_ITEMS:
                region = scrshot_img.crop((left, top, right, bottom))
                if item_exists(region):
                    num_bottom = top + 10
                    num_top = num_bottom - ITEM_HEIGHT
                    num_left = (left + right - ITEM_BG_WIDTH) // 2
                    num_right = num_left + ITEM_PRICE_WIDTH

                    if dddd is not None:
                        num_region = scrshot_img.crop(
                            (num_left, num_top, num_right, num_bottom)
                        )

                        try:
                            num_region.save(f"{text}-num.png")
                            result = int(dddd.classification(num_region))
                        except Exception as e:
                            logger.error(f"{e}")
                            result = 1
                        found_items[text] = result

            confidence: np.float64
            kept += 1

        # must have one of valuable thing
        if pic is not None or (set(found_items) - set(ADDITION_ITEMS)):

            def proc_item(p):
                k, v = p
                return f"{ALIAS_MAP.get(k, k)}{v}"

            found_things = "，".join(
                map(
                    proc_item,
                    sorted(
                        found_items.items(),
                        key=lambda p: (TARGET_ITEMS + ADDITION_ITEMS).index(p[0]),
                    ),
                )
            )
            if found_things:
                logger.info(f"发现物品: {found_things}")
                if pic is None:
                    # TODO: push to QQ group?
                    pass

            if SAVE_SCREENSHOTS or pic is not None:
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
    reader = init_general_ocr()
    num_reader = init_ddddocr()

    logger.info("程序启动，立即执行一次 OCR")
    run_ocr(reader, dddd=num_reader)

    while True:
        sleep_until_next_10min()
        run_ocr(reader, dddd=num_reader)


if __name__ == "__main__":
    main()
