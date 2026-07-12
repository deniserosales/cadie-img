from PIL import Image

from core.presets import PADDING_RATIO


def crop_and_frame(
    image: Image.Image,
    bbox: tuple[int, int, int, int] | None,
    canvas_size: int = 1080,
) -> Image.Image:
    """
    Crop the original image to a square region centered on bbox with a
    PADDING_RATIO margin on each side. Operates on the original photo
    directly — the background is preserved exactly as shot, never removed
    or replaced.

    Only downscales to (canvas_size, canvas_size) when the crop is larger
    than that; a crop already at or below canvas_size keeps its native
    resolution, since upscaling only degrades quality without improving it.

    If bbox is None (nothing segmented), the whole image is treated as the
    content. If the ideal square would spill past the image edges, the crop
    is shifted inward to fit — it is never shrunk below what the source
    photo allows, and no pixels are invented beyond the frame.
    """
    img_w, img_h = image.size

    if bbox is None:
        bbox = (0, 0, img_w, img_h)
    left, upper, right, lower = bbox

    content_w = right - left
    content_h = lower - upper
    cx = (left + right) / 2
    cy = (upper + lower) / 2

    fit_fraction = 1 - 2 * PADDING_RATIO
    side = max(content_w, content_h) / fit_fraction
    # The photo itself caps how much margin is available — cap instead of
    # inventing pixels beyond its edges. Rounded to an int up front so the
    # crop box below is exactly square, not off-by-one from independent
    # rounding of each edge.
    side = round(min(side, img_w, img_h))

    crop_left = round(max(0, min(cx - side / 2, img_w - side)))
    crop_upper = round(max(0, min(cy - side / 2, img_h - side)))
    crop_box = (crop_left, crop_upper, crop_left + side, crop_upper + side)

    cropped = image.crop(crop_box)
    if cropped.width > canvas_size:
        return cropped.resize((canvas_size, canvas_size), Image.LANCZOS)
    return cropped
