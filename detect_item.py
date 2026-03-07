from PIL import Image


def item_exists(img: Image.Image):
    return (232, 238, 255, 255) in img.getdata()


def _test():
    exists = Image.open("test/existing.png")
    not_exists = Image.open("test/non-exists.png")

    assert item_exists(exists)
    assert not item_exists(not_exists)

    print("test passed!")


if "__main__" == __name__:
    _test()
