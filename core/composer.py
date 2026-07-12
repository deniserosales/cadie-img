from PIL import Image

from core.presets import PADDING_RATIO


def crop_and_frame(
    image: Image.Image,
    bbox: tuple[int, int, int, int] | None,
    canvas_size: int = 1080,
) -> Image.Image:
    """
    Crop the original image to a square region centered on bbox with a
    PADDING_RATIO margin on each side, then resize to
    (canvas_size, canvas_size). Operates on the original photo directly —
    the background is preserved exactly as shot, never removed or replaced.

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
    # inventing pixels beyond its edges.
    side = min(side, img_w, img_h)

    crop_left = max(0, min(cx - side / 2, img_w - side))
    crop_upper = max(0, min(cy - side / 2, img_h - side))
    crop_box = (
        round(crop_left),
        round(crop_upper),
        round(crop_left + side),
        round(crop_upper + side),
    )

    cropped = image.crop(crop_box)
    return cropped.resize((canvas_size, canvas_size), Image.LANCZOS)
