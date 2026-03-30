from PIL import Image


def item_exists(img: Image.Image):
    for pixel in img.getdata():
        if pixel in [
            (207, 212, 227, 255),
            (232, 237, 255, 255),
            (232, 238, 255, 255),
            (233, 237, 255, 255),
            (233, 238, 255, 255),
        ]:
            return True
    return False
