from PIL import Image

from core.presets import BACKGROUND_COLOR, PADDING_RATIO


def center_on_canvas(
    image: Image.Image,
    canvas_width: int = 1080,
    canvas_height: int = 1080,
) -> Image.Image:
    """
    Crop to content bounding box, scale to fit within the padded area preserving
    aspect ratio, then paste centered on a BACKGROUND_COLOR canvas.

    The fit area is canvas dimensions * (1 - 2 * PADDING_RATIO), leaving
    PADDING_RATIO as a margin on each side. Returns RGBA of exactly
    (canvas_width, canvas_height).
    """
    image = image.convert("RGBA")

    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    fit_fraction = 1 - 2 * PADDING_RATIO
    max_w = round(canvas_width * fit_fraction)
    max_h = round(canvas_height * fit_fraction)

    scale = min(max_w / image.width, max_h / image.height)
    new_w = round(image.width * scale)
    new_h = round(image.height * scale)
    image = image.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (canvas_width, canvas_height), (*BACKGROUND_COLOR, 255))
    x = (canvas_width - new_w) // 2
    y = (canvas_height - new_h) // 2
    canvas.paste(image, (x, y), image)
    return canvas
