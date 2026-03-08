from fknc_adb_helper.utils import fetch_screenshot

with open("test/new.png", "wb") as f:
    f.write(fetch_screenshot())
