import easyocr
import ddddocr
import numpy as np
from PIL import Image

from loguru import logger


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
