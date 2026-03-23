from io import BytesIO

from PIL import Image

from fknc_adb_helper.utils import take_screenshot, WEATHER_RECT

pic = take_screenshot()
img = Image.open(BytesIO(pic))
img.crop(WEATHER_RECT).save("weather/_.png")
