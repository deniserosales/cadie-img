import io
import zipfile

from PIL import Image

from core.presets import WEBP_METHOD, WEBP_QUALITY


def pack_to_zip(
    images: list[tuple[str, Image.Image]],
    fmt: str = "WEBP",
) -> bytes:
    """
    Pack (filename, PIL Image) pairs into a ZIP archive.
    fmt: "WEBP" or "PNG". WEBP_QUALITY/WEBP_METHOD are ignored when fmt is PNG.
    Returns ZIP contents as bytes — nothing is written to disk.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, img in images:
            img_buf = io.BytesIO()
            if fmt.upper() == "PNG":
                img.save(img_buf, format="PNG")
            else:
                img.save(img_buf, format="WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
            zf.writestr(name, img_buf.getvalue())
    return buf.getvalue()
