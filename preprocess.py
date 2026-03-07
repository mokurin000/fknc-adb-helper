import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


InputType = bytes | str | Path | Image.Image


def preprocess_image(src: InputType) -> Image.Image:
    # 读取输入
    if isinstance(src, Image.Image):
        img = src
    elif isinstance(src, bytes):
        img = Image.open(io.BytesIO(src))
    else:
        img = Image.open(src)

    img = img.convert("RGB")

    # 转灰度
    img = img.convert("L")

    # 对比度增强
    img = ImageEnhance.Contrast(img).enhance(2.0)

    # 亮度微调
    img = ImageEnhance.Brightness(img).enhance(1.1)

    # 锐化
    img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=180, threshold=2))

    # numpy 处理
    arr = np.array(img)

    # 简单自适应阈值（增强文字）
    mean = arr.mean()
    arr = np.where(arr > mean * 0.9, 255, arr * 0.5)

    arr = arr.astype(np.uint8)

    img = Image.fromarray(arr)

    return img
