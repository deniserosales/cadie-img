from PIL import Image, ImageEnhance


def enhance_image(
    image: Image.Image,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0,
) -> Image.Image:
    """
    Apply brightness, contrast, saturation and sharpness adjustments to an RGBA image.
    Value 1.0 on every parameter is a no-op (returns a copy identical to the input).

    Adjustments are applied to the RGB channels only; the alpha channel is preserved
    unchanged and re-merged into the result.

    Args:
        brightness:  < 1.0 darkens, > 1.0 brightens.
        contrast:    < 1.0 flattens, > 1.0 increases contrast.
        saturation:  0.0 = greyscale, 1.0 = original, > 1.0 = more vivid.
        sharpness:   0.0 = blurred, 1.0 = original, > 1.0 = sharpened.
    """
    image = image.convert("RGBA")
    rgb = image.convert("RGB")
    _, _, _, alpha = image.split()

    if brightness != 1.0:
        rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    if contrast != 1.0:
        rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    if saturation != 1.0:
        rgb = ImageEnhance.Color(rgb).enhance(saturation)
    if sharpness != 1.0:
        rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)

    r, g, b = rgb.split()
    return Image.merge("RGBA", (r, g, b, alpha))
