from PIL import Image


def item_exists(img: Image.Image):
    for pixel in img.getdata():
        if pixel in [
            (232, 237, 255, 255),
            (232, 238, 255, 255),
        ]:
            return True
    return False


def _test():
    exists = Image.open("test/existing.png")
    exists2 = Image.open("test/existing2.png")
    not_exists = Image.open("test/non-exists.png")

    assert item_exists(exists)
    assert item_exists(exists2)
    assert not item_exists(not_exists)

    print("test passed!")


if "__main__" == __name__:
    _test()
