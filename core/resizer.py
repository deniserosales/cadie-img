from PIL import Image


def resize_image(image: Image.Image, width: int, height: int, keep_aspect: bool = True) -> Image.Image:
    """
    Resize a PIL Image to (width, height).

    keep_aspect=True  → fits within the box preserving the original ratio (no distortion).
    keep_aspect=False → stretches to exact dimensions.
    """
    if keep_aspect:
        img = image.copy()
        img.thumbnail((width, height), Image.LANCZOS)
        return img
    return image.resize((width, height), Image.LANCZOS)
