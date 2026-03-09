from fknc_adb_helper.utils import take_screenshot

with open("test/new.png", "wb") as f:
    f.write(take_screenshot())
