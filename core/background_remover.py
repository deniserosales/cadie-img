import io

import numpy as np
from PIL import Image
from rembg import new_session, remove

_sessions: dict[str, object] = {}


def _get_session(model_name: str) -> object:
    if model_name not in _sessions:
        _sessions[model_name] = new_session(model_name)
    return _sessions[model_name]


def remove_background(
    image: Image.Image,
    model_name: str = "isnet-general-use",
    alpha_threshold: int = 128,
) -> tuple[Image.Image, float]:
    """
    Remove background using rembg and clean up the alpha mask.

    alpha_threshold: pixels with alpha < this value become fully transparent.
                     Eliminates faint shadow halos left by the model (default 128).

    Returns (result_image, content_width_ratio) where content_width_ratio is the
    width of the segmented content bbox divided by the original image width.
    """
    session = _get_session(model_name)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    result_bytes = remove(buf.getvalue(), session=session)
    result = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

    # Alpha threshold: zero out semi-transparent shadows and halos
    if alpha_threshold > 0:
        r, g, b, a = result.split()
        a_arr = np.array(a, dtype=np.uint8)
        a_arr[a_arr < alpha_threshold] = 0
        result = Image.merge("RGBA", (r, g, b, Image.fromarray(a_arr)))

    bbox = result.getbbox()
    content_width_ratio = (bbox[2] - bbox[0]) / image.width if bbox else 0.0

    return result, content_width_ratio
