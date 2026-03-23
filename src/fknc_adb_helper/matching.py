import cv2 as cv
from cv2.typing import MatLike


def match_object(
    image: MatLike,
    template: MatLike,
    threshold=0.8,
):

    res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)

    if max_val >= threshold:
        h, w = template.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        image_color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        cv.rectangle(image_color, top_left, bottom_right, (0, 255, 0), 2)

        return True
    else:
        return False
