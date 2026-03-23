from sys import argv
from io import BytesIO

from PIL import Image

from fknc_adb_helper.utils import take_screenshot, WEATHER_RECT

if len(argv) < 2:
    pic = take_screenshot()
    img = Image.open(BytesIO(pic))
else:
    img = Image.open(argv[1])

img.crop(WEATHER_RECT).save("weather/_.png")
