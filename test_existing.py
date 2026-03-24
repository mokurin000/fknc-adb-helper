from PIL import Image

from fknc_adb_helper.detect_item import item_exists


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
