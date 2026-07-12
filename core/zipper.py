import io
import zipfile

from PIL import Image

from core.presets import WEBP_LOSSLESS, WEBP_METHOD, WEBP_QUALITY


def pack_to_zip(
    images: list[tuple[str, Image.Image]],
    fmt: str = "WEBP",
) -> bytes:
    """
    Pack (filename, PIL Image) pairs into a ZIP archive.
    fmt: "WEBP" or "PNG". WEBP_QUALITY/WEBP_METHOD are ignored when fmt is PNG.
    Reuses each image's icc_profile from img.info if present, so downstream
    color rendering matches the original photo. Returns ZIP contents as
    bytes — nothing is written to disk.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, img in images:
            img_buf = io.BytesIO()
            icc_profile = img.info.get("icc_profile")
            save_kwargs: dict = {}
            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile
            if fmt.upper() == "PNG":
                img.save(img_buf, format="PNG", **save_kwargs)
            else:
                img.save(
                    img_buf,
                    format="WEBP",
                    quality=WEBP_QUALITY,
                    method=WEBP_METHOD,
                    lossless=WEBP_LOSSLESS,
                    **save_kwargs,
                )
            zf.writestr(name, img_buf.getvalue())
    return buf.getvalue()
