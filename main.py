import easyocr
import numpy as np


def init_reader() -> easyocr.Reader:
    reader = easyocr.Reader(["ch_sim", "en"])
    return reader


reader = init_reader()
result = reader.readtext("Telegram_gvC1JfcFZ3.png")

for coords, text, confidence in result:
    confidence: np.float64
    print(text, f"{confidence * 100:.02f}%")
