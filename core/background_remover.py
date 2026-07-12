import io

import numpy as np
from PIL import Image
from rembg import new_session, remove

_sessions: dict[str, object] = {}


def _get_session(model_name: str) -> object:
    if model_name not in _sessions:
        _sessions[model_name] = new_session(model_name)
    return _sessions[model_name]


def detect_content_bbox(
    image: Image.Image,
    model_name: str = "isnet-general-use",
    alpha_threshold: int = 128,
) -> tuple[int, int, int, int] | None:
    """
    Segment the piece with rembg and return the bounding box of its alpha
    mask, in the original image's pixel coordinates. The segmentation
    cutout itself is discarded — only its shape is used, so the original
    photo's background is never altered.

    alpha_threshold: pixels with alpha below this value are treated as
    background, filtering out faint halos left by the segmentation model.

    Returns (left, upper, right, lower), or None if nothing was segmented.
    """
    session = _get_session(model_name)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    result_bytes = remove(buf.getvalue(), session=session)
    alpha = Image.open(io.BytesIO(result_bytes)).convert("RGBA").split()[3]

    if alpha_threshold > 0:
        a_arr = np.array(alpha, dtype=np.uint8)
        a_arr[a_arr < alpha_threshold] = 0
        alpha = Image.fromarray(a_arr)

    return alpha.getbbox()
