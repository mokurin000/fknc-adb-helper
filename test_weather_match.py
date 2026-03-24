import os
import cv2 as cv
from loguru import logger

# Import the updated match_object that supports masks
from fknc_adb_helper.matching import match_object


def load_template_with_mask(weather_name: str):
    """Load weather template + mask from PNG (supports transparency)"""
    template_path = f"weather/{weather_name}.png"

    icon = cv.imread(template_path, cv.IMREAD_UNCHANGED)
    if icon is None:
        raise OSError(f"Failed to load template: {template_path}")

    if len(icon.shape) == 3 and icon.shape[2] == 4:  # RGBA image
        bgr = icon[:, :, :3]
        alpha = icon[:, :, 3]
        template = cv.cvtColor(bgr, cv.COLOR_BGR2GRAY)
        # Create mask: ignore nearly transparent pixels
        _, mask = cv.threshold(alpha, 20, 255, cv.THRESH_BINARY)
    else:
        template = (
            cv.cvtColor(icon, cv.COLOR_BGR2GRAY) if len(icon.shape) == 3 else icon
        )
        mask = None

    return template, mask


def test_match(
    weather: str,
    test_weather: str = None,
    threshold: float = 0.85,
):
    """Test matching with mask support"""
    # Load template + mask
    template, mask = load_template_with_mask(weather)

    # Load test image
    test_file = test_weather or weather
    image_path = f"weather-test/{test_file}.png"

    image = cv.imread(image_path, cv.IMREAD_COLOR)
    if image is None:
        raise OSError(f"Failed to load test image: {image_path}")

    # Crop to weather area (1920x1080 resolution)
    image = image[24:69, 572:780]
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    return match_object(
        image=gray_image,
        template=template,
        mask=mask,
        threshold=threshold,
    )


if __name__ == "__main__":
    # Get all test images
    test_pics = [
        w.removesuffix(".png") for w in os.listdir("weather-test") if w.endswith(".png")
    ]

    print(f"Starting weather matching test with {len(test_pics)} images...\n")

    for weather in test_pics:
        try:
            result = test_match(weather)
            assert result, f"{weather} should match itself"
            logger.info(f"{weather} matching passed!")
        except Exception as e:
            logger.error(f"{weather} matching failed! Error: {e}")

        # Test that it does NOT match other weather icons
        others = set(test_pics) - {weather}
        for other in others:
            try:
                result = test_match(weather, test_weather=other)
                assert not result, f"{weather} should NOT match {other}"
                logger.info(f"{weather} vs {other} -> correctly not matched")
            except Exception as e:
                logger.error(f"{weather} vs {other} test failed! Error: {e}")

    logger.info("matching test completed!")
