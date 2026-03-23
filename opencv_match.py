import os

import cv2 as cv
import matplotlib.pyplot as plt


def match_weather(weather: str, threshold=0.8, show=True):
    template = cv.imread(f"weather/{weather}.png", cv.IMREAD_GRAYSCALE)
    image = cv.imread(f"weather-test/{weather}.png", cv.IMREAD_GRAYSCALE)

    if template is None or image is None:
        print("图片读取失败")
        return False

    res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)

    if max_val >= threshold:
        h, w = template.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        image_color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        cv.rectangle(image_color, top_left, bottom_right, (0, 255, 0), 2)

        if show:
            image_rgb = cv.cvtColor(image_color, cv.COLOR_BGR2RGB)

            plt.imshow(image_rgb)
            plt.title(f"Match: {weather} ({max_val:.3f})")
            plt.axis("off")
            plt.show(block=False)
            plt.waitforbuttonpress()

        return True
    else:
        return False


if __name__ == "__main__":
    for weather in os.listdir("weather-test"):
        weather = weather.removesuffix(".png")
        match_weather(weather)
