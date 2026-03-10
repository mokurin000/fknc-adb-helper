import io
import os
import time
from datetime import datetime

import ddddocr
import easyocr
import numpy as np
from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from fknc_adb_helper.bot import send_message
from fknc_adb_helper.utils import (
    fetch_screenshot,
    init_ddddocr,
    init_general_ocr,
    sleep_until_next_10min,
)
from fknc_adb_helper.detect_item import item_exists

SAVE_SCREENSHOTS = False

ITEM_BG_WIDTH = 165
ITEM_PRICE_WIDTH = 50
ITEM_HEIGHT = 40

TARGET_SEEDS = [
    "草莓",
    "松树",
    "向日葵",
    "大王菊",
    "蟠桃",
    "月核树",
    "液光藤",
    "月影梅",
    "幻月花",
]

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
    "引雷针",
    "火盆",
    "造雪机",
    "唤醒机",
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

font = ImageFont.truetype("msyh.ttc", 20)  # 微软雅黑

logger.add(
    "ocr.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
)


def run_ocr(
    reader: easyocr.Reader,
    screenshot: bytes,
    dddd: ddddocr.DdddOcr = None,
    recognize_seeds: bool = False,
    min_confidence: float = 0.7,
) -> dict[str, int | tuple[()]]:
    """
    调用OCR引擎，提取有效物品及其数量

    若 `dddd` 引擎未加载，则不记录其数量，设置为空元组。
    """
    found_items: dict[str] = {}
    pic_type = "seed" if recognize_seeds else "item"

    try:
        scrshot_img = Image.open(io.BytesIO(screenshot))
        scrshot_img.save("screenshot.png")

        result = reader.readtext("screenshot.png")

        ts = datetime.now().strftime("%Y-%m-%d-%H_%M")
        filename = f"pics/{ts}-{pic_type}-result.png"
        scr_filename = f"pics/{ts}-{pic_type}-screenshot.png"

        img = scrshot_img.copy()
        draw = ImageDraw.Draw(img)

        for coords, text, confidence in result:
            pts = [(int(x), int(y)) for x, y in coords]

            draw.polygon(pts, outline="red", width=3)

            x, y = pts[0]
            draw.text(
                (x, y - 20),
                f"{text} {confidence * 100:.1f}%",
                fill="red",
                font=font,
            )

            if confidence < min_confidence:
                continue

            top_left, _, bottom_right, _ = pts
            left, top = top_left
            right, bottom = bottom_right

            if (
                recognize_seeds
                and text.endswith("种子")
                and text.removesuffix("种子") in TARGET_SEEDS
            ) or (text in TARGET_ITEMS + ADDITION_ITEMS):
                region = scrshot_img.crop((left, top, right, bottom))
                if item_exists(region):
                    if dddd is not None:
                        num_bottom = top + 10
                        num_top = num_bottom - ITEM_HEIGHT
                        num_left = (left + right - ITEM_BG_WIDTH) // 2
                        num_right = num_left + ITEM_PRICE_WIDTH

                        num_region = scrshot_img.crop(
                            (num_left, num_top, num_right, num_bottom)
                        )

                        try:
                            result = int(dddd.classification(num_region))
                        except Exception as e:
                            logger.error(f"{e}")
                            result = 1
                        found_items[text] = result
                    else:
                        found_items[text] = ()

            confidence: np.float64

        if SAVE_SCREENSHOTS:
            img.save(filename)
            with open(scr_filename, "wb") as f:
                f.write(screenshot)

    except Exception as e:
        logger.exception(f"OCR 任务失败: {e}")

    return found_items


def alias_mapping(p):
    k, v = p
    return f"{ALIAS_MAP.get(k, k)}{v}"


def call_ocr(reader: easyocr.Reader, num_reader: ddddocr.DdddOcr):
    seeds, tools = fetch_screenshot(skip_sleep=False)

    found_seeds = run_ocr(
        reader,
        screenshot=seeds,
        dddd=None,
        recognize_seeds=True,
        min_confidence=0.08,
    )
    found_tools = run_ocr(
        reader,
        screenshot=tools,
        dddd=num_reader,
    )

    tools_string = ""
    seeds_string = ""

    if found_seeds:
        seeds_string = "，".join(found_seeds.values())
        logger.info(f"发现种子: {seeds_string}")

    # must have one of valuable thing
    if set(found_tools.values()) - set(ADDITION_ITEMS):
        tools_string = "，".join(
            map(
                alias_mapping,
                sorted(
                    found_tools.items(),
                    key=lambda p: (TARGET_ITEMS + ADDITION_ITEMS).index(p[0]),
                ),
            )
        )
        if tools_string:
            logger.info(f"发现物品: {tools_string}")

    if seeds_string or tools_string:
        try:
            send_message(
                f"商店刷新：\n{seeds_string}\n{tools_string}".replace(
                    "\n\n", "\n"
                ).strip()
            )
        except Exception as e:
            logger.error(f"推送失败：{e}")


def main():
    time1 = time.monotonic()
    reader = init_general_ocr()
    num_reader = init_ddddocr()
    time2 = time.monotonic()

    logger.info(f"初始化完成，耗时{time2 - time1:.2f}s")
    while True:
        sleep_until_next_10min()
        call_ocr(
            reader=reader,
            num_reader=num_reader,
        )


if __name__ == "__main__":
    main()
