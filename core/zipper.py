import io
import zipfile

from PIL import Image


def pack_to_zip(
    images: list[tuple[str, Image.Image]],
    fmt: str = "WEBP",
    webp_quality: int = 90,
) -> bytes:
    """
    Pack (filename, PIL Image) pairs into a ZIP archive.
    fmt: "WEBP" or "PNG". webp_quality is ignored when fmt is PNG.
    Returns ZIP contents as bytes — nothing is written to disk.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, img in images:
            img_buf = io.BytesIO()
            if fmt.upper() == "PNG":
                img.save(img_buf, format="PNG")
            else:
                img.save(img_buf, format="WEBP", quality=webp_quality)
            zf.writestr(name, img_buf.getvalue())
    return buf.getvalue()
