import io
import os
import sys
import time
from enum import Enum
from subprocess import CalledProcessError
from datetime import datetime

import ddddocr
import easyocr
from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from fknc_adb_helper.bot import send_message
from fknc_adb_helper.utils import (
    common_ocr,
    fetch_screenshot,
    fetch_weather,
    init_ddddocr,
    init_general_ocr,
    is_eggy_party,
    sleep_until_next_10min,
)
from fknc_adb_helper.detect_item import item_exists

# left, top, right, bottom (pixel)
# for 1920x1080
STORE_RECT = (1149, 345, 1149 + 593, 345 + 688)
WEATHER_RECT = (468, 103, 1084, 177)

SAVE_SCREENSHOTS = False
SAVE_RESULT = True

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
    "造型喷雾",
    "月球白银洒水器",
    "白银洒水器",
    "月球标准洒水器",
]

TARGET_WEATHER = {
    "雾",
    "荧光",
    "彩虹",
    "霓虹",
    "日蚀",
    "沙尘暴",
    "流星雨",
    "陨石雨",
    "太阳耀斑",
}

ADDITION_ITEMS = [
    "农田置换卡",
    "引雷针",
    "火盆",
    "造雪机",
    "唤醒机",
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


class RecognizeType(Enum):
    ITEM = "item"
    SEED = "seed"
    WEATHER = "weather"


def validate_text(text: str, rec_type: RecognizeType) -> bool:
    match rec_type:
        case RecognizeType.ITEM:
            return text in TARGET_ITEMS + ADDITION_ITEMS
        case RecognizeType.SEED:
            return text.endswith("种子") and text.removesuffix("种子") in TARGET_SEEDS
        case RecognizeType.WEATHER:
            return True


def run_ocr(
    reader: easyocr.Reader,
    screenshot: bytes,
    dddd: ddddocr.DdddOcr = None,
    recognize_type: RecognizeType = RecognizeType.ITEM,
    min_confidence: float = 0.7,
    crop_rect: tuple[int, int, int, int] = None,
) -> dict[str, int | tuple[()]]:
    """
    调用OCR引擎，提取有效物品及其数量

    若 `dddd` 引擎未加载，则不记录其数量，设置为空元组。

    :param: crop_rect left, top, right, bottom 绝对像素坐标
    """
    found_items: dict[str] = {}

    try:
        scrshot_img = Image.open(io.BytesIO(screenshot))
        scrshot_img = scrshot_img.crop(crop_rect or STORE_RECT)
        result = common_ocr(
            reader=reader,
            pic=scrshot_img,
        )

        ts = datetime.now().strftime("%Y-%m-%d-%H_%M")
        filename = f"pics/{ts}-{recognize_type.value}-result.png"
        scr_filename = f"pics/{ts}-{recognize_type.value}-screenshot.png"

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

            text = text.replace("孑", "子").replace("士", "土")
            if validate_text(
                text=text,
                rec_type=recognize_type,
            ):
                region = scrshot_img.crop((left, top, right, bottom))
                if recognize_type == RecognizeType.WEATHER:
                    found_items[text] = ()
                elif item_exists(region):
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

        if SAVE_RESULT:
            img.save(filename)
        if SAVE_SCREENSHOTS:
            scrshot_img.save(scr_filename)

    except Exception as e:
        logger.exception(f"OCR 任务失败: {e}")

    return found_items


def alias_mapping(p):
    k, v = p
    return f"{ALIAS_MAP.get(k, k)}{v}"


def call_ocr(reader: easyocr.Reader, num_reader: ddddocr.DdddOcr):
    try:
        assert is_eggy_party()
        seeds, tools = fetch_screenshot()
    except AssertionError:
        logger.error("当前活动非蛋仔派对，跳过处理！")
        return
    except CalledProcessError | Exception as e:
        logger.error(f"截图失败：{e}")
        return

    found_seeds = run_ocr(
        reader,
        screenshot=seeds,
        dddd=None,
        recognize_type=RecognizeType.SEED,
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
        seeds_string = "，".join(
            map(lambda s: str.removesuffix(s, "种子"), found_seeds.keys())
        )

    # must have one of valuable thing
    if set(found_tools.keys()) & set(TARGET_ITEMS):
        tools_string = "，".join(
            map(
                alias_mapping,
                sorted(
                    found_tools.items(),
                    key=lambda p: (TARGET_ITEMS + ADDITION_ITEMS).index(p[0]),
                ),
            )
        )

    logger.info(f"识别结果：{list(found_seeds.items())} | {list(found_tools.items())}")

    msg = ""

    if seeds_string or tools_string:
        msg = "\n".join(
            filter(
                str.__len__,
                f"{seeds_string}\n{tools_string}".split("\n"),
            )
        )

        try:
            send_message(msg)
        except Exception as e:
            logger.error(f"推送失败：{e}")

    weather = fetch_weather()
    found_weather = run_ocr(
        reader,
        screenshot=weather,
        min_confidence=0.5,
        crop_rect=WEATHER_RECT,
        recognize_type=RecognizeType.WEATHER,
    )

    weather_string = ""
    if found_weather:
        for weather_text in found_weather:
            if weather_text in TARGET_WEATHER:
                weather_string = weather_text
                break

    if weather_string:
        msg = weather_string.strip()
        try:
            send_message(msg)
        except Exception as e:
            logger.error(f"推送失败：{e}")


def main():
    logger.add(
        "ocr.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        enqueue=True,
    )

    time1 = time.monotonic()
    reader = init_general_ocr()
    num_reader = init_ddddocr()
    time2 = time.monotonic()

    logger.info(f"初始化完成，耗时{time2 - time1:.2f}s")

    if "--skip-first-sleep" not in sys.argv:
        sleep_until_next_10min()

    while True:
        call_ocr(
            reader=reader,
            num_reader=num_reader,
        )
        sleep_until_next_10min()


if __name__ == "__main__":
    main()
