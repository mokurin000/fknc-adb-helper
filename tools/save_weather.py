from sys import argv
from io import BytesIO

from PIL import Image

from fknc_adb_helper.utils import take_screenshot, WEATHER_RECT

if len(argv) < 2:
    exit(1)

name = argv[1]

if len(argv) < 3:
    pic = take_screenshot()
    img = Image.open(BytesIO(pic))
else:
    img = Image.open(argv[2])

img.save(f"weather-test/{name}.png")
img.crop(WEATHER_RECT).save(f"weather/{name}.png")
