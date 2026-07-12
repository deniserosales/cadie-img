from PIL import Image, ImageFilter

from core.presets import SHADOW_BLUR, SHADOW_OFFSET, SHADOW_OPACITY


def generate_shadow(
    alpha: Image.Image,
    offset: tuple[int, int] = SHADOW_OFFSET,
    blur: int = SHADOW_BLUR,
    opacity: float = SHADOW_OPACITY,
) -> Image.Image:
    """
    Build an RGBA drop-shadow layer from a piece's alpha mask.

    Copies the mask, fills it black, shifts it by offset, blurs it, then
    scales the alpha channel to opacity. Returns an RGBA image the same
    size as `alpha`, meant to be composited beneath the piece it came from.
    """
    shifted = Image.new("L", alpha.size, 0)
    shifted.paste(alpha, offset)
    blurred = shifted.filter(ImageFilter.GaussianBlur(blur))

    if opacity != 1.0:
        blurred = blurred.point(lambda a: round(a * opacity))

    shadow = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    shadow.putalpha(blurred)
    return shadow
