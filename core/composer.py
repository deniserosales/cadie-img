from PIL import Image


def center_on_canvas(
    image: Image.Image,
    canvas_width: int = 1080,
    canvas_height: int = 1080,
    padding: float = 0.75,
) -> Image.Image:
    """
    Crop to content bounding box, scale to fit within padding*canvas preserving
    aspect ratio, then paste centered on a transparent canvas.

    padding: fraction of canvas dimensions used as the fit area (0.9 = 90%,
    leaves ~5% margin on each side). Returns RGBA of exactly (canvas_width, canvas_height).
    """
    image = image.convert("RGBA")

    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    max_w = round(canvas_width * padding)
    max_h = round(canvas_height * padding)

    scale = min(max_w / image.width, max_h / image.height)
    new_w = round(image.width * scale)
    new_h = round(image.height * scale)
    image = image.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    x = (canvas_width - new_w) // 2
    y = (canvas_height - new_h) // 2
    canvas.paste(image, (x, y), image)
    return canvas
