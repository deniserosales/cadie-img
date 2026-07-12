import html
import os
import tempfile
from pathlib import Path

import gradio as gr
from PIL import Image

from core.background_remover import remove_background
from core.composer import center_on_canvas
from core.enhancer import enhance_image
from core.presets import WEBP_METHOD, WEBP_QUALITY
from core.zipper import pack_to_zip

# ── Bluppimart design system ───────────────────────────────────────────────────

_CSS = (Path(__file__).parent / "bluppimart.css").read_text()

# Full 11-stop blue scale for #2ca9e1.
# Replaces Gradio's default violet/purple on every accent (sliders, radios,
# checkboxes, focus rings, progress bars).
_BLUE = gr.themes.Color(
    c50="#f0f9fd",
    c100="#d8effa",
    c200="#b3e0f5",
    c300="#7dcbee",
    c400="#4db8e7",
    c500="#2ca9e1",
    c600="#1d8fc2",
    c700="#1675a3",
    c800="#0f5c84",
    c900="#094566",
    c950="#062e44",
)

# Neutral scale for consistent dark-mode greys.
_NEUTRAL = gr.themes.Color(
    c50="#f9fafb",
    c100="#f0f2f5",
    c200="#e1e5ea",
    c300="#c5ccd6",
    c400="#9aa3ae",
    c500="#6b7280",
    c600="#4b5563",
    c700="#374151",
    c800="#1f2937",
    c900="#111827",
    c950="#0d1117",
)

_THEME = gr.themes.Soft(
    primary_hue=_BLUE,
    neutral_hue=_NEUTRAL,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
).set(
    # ── Light mode ────────────────────────────────────────────────────────────
    body_background_fill="#f8f9fa",
    block_background_fill="#ffffff",
    panel_background_fill="#ffffff",
    input_background_fill="#ffffff",
    input_background_fill_hover="#ffffff",
    input_background_fill_focus="#ffffff",
    color_accent="#2ca9e1",
    color_accent_soft="rgba(44,169,225,0.18)",
    border_color_accent="#2ca9e1",
    border_color_primary="#dddddd",
    body_text_color="#333333",
    body_text_color_subdued="#555555",
    block_info_text_color="#666666",
    block_label_text_color="#555555",
    block_label_text_weight="600",
    block_title_text_color="#333333",
    block_title_text_weight="600",
    slider_color="#2ca9e1",
    input_border_color="#dddddd",
    input_border_color_hover="#dddddd",
    input_border_color_focus="#2ca9e1",
    input_shadow_focus="0 0 0 3px rgba(44,169,225,0.18)",
    input_radius="8px",
    input_padding="0.75rem",
    block_radius="16px",
    block_border_color="#e9ecef",
    block_border_width="1px",
    block_shadow="0 2px 8px rgba(0,0,0,0.05)",
    container_radius="16px",
    # Primary button
    button_primary_background_fill="#2ca9e1",
    button_primary_background_fill_hover="#2ca9e1",
    button_primary_text_color="#fffbf5",
    button_primary_text_color_hover="#fffbf5",
    button_primary_border_color="#2ca9e1",
    button_primary_border_color_hover="#2ca9e1",
    button_primary_shadow_hover="0 4px 14px rgba(44,169,225,0.4)",
    # Secondary button
    button_secondary_background_fill="#ffffff",
    button_secondary_background_fill_hover="#ffffff",
    button_secondary_text_color="#555555",
    button_secondary_text_color_hover="#2ca9e1",
    button_secondary_border_color="#dddddd",
    button_secondary_border_color_hover="#2ca9e1",
    # Button sizing — tool ergonomics
    button_large_radius="8px",
    button_medium_radius="8px",
    button_small_radius="8px",
    button_large_text_size="1.1rem",
    button_large_text_weight="600",
    button_medium_text_size="1rem",
    button_medium_text_weight="600",
    button_small_text_size="0.85rem",
    button_small_text_weight="500",
    button_large_padding="0.75rem 1.5rem",
    button_transform_hover="translateY(-1px)",
    button_transition="transform 0.15s ease, box-shadow 0.15s ease",

    # ── Dark mode ─────────────────────────────────────────────────────────────
    # Backgrounds
    body_background_fill_dark="#0f1419",
    block_background_fill_dark="#1a2027",
    panel_background_fill_dark="#1a2027",
    input_background_fill_dark="#212830",
    input_background_fill_hover_dark="#212830",
    input_background_fill_focus_dark="#212830",
    background_fill_primary_dark="#1a2027",
    background_fill_secondary_dark="#212830",
    # Text — all verified ≥ 4.5:1 contrast against #1a2027
    body_text_color_dark="#e9ecef",           # 14.8:1 ✓
    body_text_color_subdued_dark="#adb5bd",   #  7.4:1 ✓
    block_info_text_color_dark="#868e96",     #  5.1:1 ✓
    block_label_text_color_dark="#cbd5e0",    #  9.8:1 ✓
    block_title_text_color_dark="#e9ecef",    # 14.8:1 ✓
    accordion_text_color_dark="#e9ecef",
    # Borders
    block_border_color_dark="#2d3748",
    border_color_primary_dark="#2d3748",
    input_border_color_dark="#2d3748",
    input_border_color_hover_dark="#2d3748",
    input_border_color_focus_dark="#2ca9e1",
    input_shadow_focus_dark="0 0 0 3px rgba(44,169,225,0.25)",
    # Shadow
    block_shadow_dark="0 2px 12px rgba(0,0,0,0.4)",
    # Primary button: unchanged (blue works great on dark)
    button_primary_background_fill_dark="#2ca9e1",
    button_primary_background_fill_hover_dark="#2ca9e1",
    button_primary_text_color_dark="#fffbf5",
    button_primary_text_color_hover_dark="#fffbf5",
    button_primary_border_color_dark="#2ca9e1",
    button_primary_border_color_hover_dark="#2ca9e1",
    button_primary_shadow_hover_dark="0 4px 16px rgba(44,169,225,0.5)",
    # Secondary button dark
    button_secondary_background_fill_dark="#212830",
    button_secondary_background_fill_hover_dark="#212830",
    button_secondary_text_color_dark="#adb5bd",
    button_secondary_text_color_hover_dark="#2ca9e1",
    button_secondary_border_color_dark="#2d3748",
    button_secondary_border_color_hover_dark="#2ca9e1",
    # Slider
    slider_color_dark="#2ca9e1",
    # Error/neutral dark
    error_background_fill_dark="rgba(220,53,69,0.12)",
    error_border_color_dark="rgba(220,53,69,0.3)",
    error_text_color_dark="#fca5a5",
)

# ── JS: force dark mode on load ───────────────────────────────────────────────
_INIT_JS = "() => { document.documentElement.classList.add('dark'); }"

# ── SVG icon helpers ───────────────────────────────────────────────────────────

def _ico(paths: str, size: int = 14) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )

_ICO_UPLOAD = _ico(
    '<polyline points="16 16 12 12 8 16"/>'
    '<line x1="12" y1="12" x2="12" y2="21"/>'
    '<path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>'
)
_ICO_FORMAT = _ico(
    '<rect x="3" y="3" width="18" height="18" rx="2"/>'
    '<path d="M3 9h18"/><path d="M9 21V9"/>'
)
_ICO_ADJUST = _ico(
    '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/>'
    '<line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/>'
    '<line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>'
    '<line x1="1" y1="14" x2="7" y2="14"/>'
    '<line x1="9" y1="8" x2="15" y2="8"/>'
    '<line x1="17" y1="16" x2="23" y2="16"/>'
)
_ICO_RESULTS = _ico(
    '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
    '<polyline points="22 4 12 14.01 9 11.01"/>',
    size=15,
)
_ICO_DOWNLOAD = _ico(
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="7 10 12 15 17 10"/>'
    '<line x1="12" y1="15" x2="12" y2="3"/>'
)

def _label(icon: str, text: str) -> str:
    return f'<div class="bp-section-label">{icon}<span>{text}</span></div>'

def _files_to_gallery(paths: list) -> tuple[list, list]:
    """Build gallery thumbnails and the subset of paths that opened cleanly.

    Returns (gallery_items, valid_paths) — callers must persist valid_paths
    back into accumulated_files so the gallery's displayed order always
    matches the state list 1:1 (deletion is index-based against that list).
    """
    items, valid = [], []
    for p in paths:
        try:
            items.append((Image.open(p), Path(p).name))
            valid.append(p)
        except Exception:
            pass
    return items, valid

def _status_html(msg: str, success: bool) -> str:
    safe = html.escape(msg)
    if success:
        svg = _ico(
            '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
            '<polyline points="22 4 12 14.01 9 11.01"/>',
            size=18,
        )
        return f'<div class="bp-status bp-status--success">{svg}{safe}</div>'
    svg = _ico(
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="15" y1="9" x2="9" y2="15"/>'
        '<line x1="9" y1="9" x2="15" y2="15"/>',
        size=18,
    )
    return f'<div class="bp-status bp-status--error">{svg}{safe}</div>'


# ── Preview cache helpers ──────────────────────────────────────────────────────

def _preview_on_white(image: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
    bg.paste(image, mask=image.split()[3])
    return bg.convert("RGB")


def _prepare_cache(
    files: list,
    canvas_width: int,
    canvas_height: int,
):
    _hidden_status = gr.update(value="", visible=False)
    if not files:
        return None, None, None, _hidden_status
    try:
        img = Image.open(files[0])
        bgremoved, _ = remove_background(img)
        centered = center_on_canvas(bgremoved, int(canvas_width), int(canvas_height))
        return bgremoved, centered, _preview_on_white(centered), _hidden_status
    except Exception:
        return None, None, None, _hidden_status


def _recenter_preview(
    bgremoved: Image.Image | None,
    canvas_width: int,
    canvas_height: int,
) -> tuple[Image.Image | None, Image.Image | None]:
    if bgremoved is None:
        return None, None
    try:
        centered = center_on_canvas(bgremoved, int(canvas_width), int(canvas_height))
        return centered, _preview_on_white(centered)
    except Exception:
        return None, None


def _enhance_preview(
    centered: Image.Image | None,
    brightness: float,
    contrast: float,
    saturation: float,
    sharpness: float,
) -> Image.Image | None:
    if centered is None:
        return None
    return _preview_on_white(enhance_image(centered, brightness, contrast, saturation, sharpness))


# ── Batch pipeline ─────────────────────────────────────────────────────────────

def process_batch(
    files: list[str],
    canvas_width: int,
    canvas_height: int,
    fmt: str,
    brightness: float,
    contrast: float,
    saturation: float,
    sharpness: float,
    progress: gr.Progress = gr.Progress(),
) -> tuple:
    if not files:
        return None, "No images uploaded.", [], [], []

    total = len(files)
    ext = "webp" if fmt.upper() == "WEBP" else "png"
    tmpdir = tempfile.mkdtemp(prefix="bluppi_")
    before_gallery, after_gallery, individual_paths, processed = [], [], [], []

    for i, file_path in enumerate(files):
        progress(i / total, desc=f"Processing image {i + 1} of {total}…")
        try:
            original = Image.open(file_path)
            before_gallery.append((original.copy(), Path(file_path).name))
            img, _ = remove_background(original)
            img = enhance_image(img, brightness, contrast, saturation, sharpness)
            img = center_on_canvas(img, int(canvas_width), int(canvas_height))
            stem = Path(file_path).stem
            out_name = f"{stem}_nobg.{ext}"
            out_path = os.path.join(tmpdir, out_name)
            save_kwargs: dict = {"format": fmt.upper()}
            if fmt.upper() == "WEBP":
                save_kwargs["quality"] = WEBP_QUALITY
                save_kwargs["method"] = WEBP_METHOD
            img.save(out_path, **save_kwargs)
            individual_paths.append(out_path)
            after_gallery.append((_preview_on_white(img), out_name))
            processed.append((out_name, img))
        except Exception as exc:
            name = Path(file_path).name
            return None, f"Error on image {i + 1} ({name}): {exc}", [], [], []

    progress(1.0, desc="Packaging ZIP…")
    zip_bytes = pack_to_zip(processed, fmt=fmt.upper())
    zip_path = os.path.join(tmpdir, "bluppi_output.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    return zip_path, f"Done! {total} image(s) processed.", before_gallery, after_gallery, individual_paths


# ── UI ─────────────────────────────────────────────────────────────────────────

def _build_ui() -> gr.Blocks:
    with gr.Blocks(title="bluppi-img") as demo:

        gr.Markdown("# bluppi-img\nRemove background · center on canvas · export.")

        bgremoved_state   = gr.State(value=None)
        centered_state    = gr.State(value=None)
        accumulated_files = gr.State(value=[])

        # ── Config zone ────────────────────────────────────────────────────
        with gr.Row():
            # ── Left: upload ───────────────────────────────────────────────
            with gr.Column(scale=2):
                gr.HTML(_label(_ICO_UPLOAD, "Upload images"), elem_classes=["bp-label-block"])
                file_input = gr.File(
                    label="Upload images",
                    file_count="multiple",
                    file_types=["image"],
                    elem_classes=["bp-upload-zone"],
                )
                # Thumbnail queue — hidden until first upload. interactive=True
                # enables Gradio's built-in per-thumbnail delete ("X") button.
                queue_gallery = gr.Gallery(
                    show_label=False,
                    columns=4,
                    height="auto",
                    object_fit="cover",
                    allow_preview=False,
                    interactive=True,
                    buttons=[],           # no share/download/fullscreen — they
                                           # overlap the per-thumbnail X at low
                                           # item counts and aren't needed here
                    visible=False,
                    elem_classes=["bp-queue-gallery"],
                )

            # ── Right: settings ────────────────────────────────────────────
            with gr.Column(scale=3):
                with gr.Row():
                    width_in  = gr.Number(label="Canvas width (px)",  value=1080, minimum=1, precision=0)
                    height_in = gr.Number(label="Canvas height (px)", value=1080, minimum=1, precision=0)

                gr.HTML(_label(_ICO_FORMAT, "Output format"), elem_classes=["bp-label-block"])
                fmt_radio = gr.Radio(
                    ["WebP", "PNG"], label="Format", value="WebP"
                )

                gr.HTML(_label(_ICO_ADJUST, "Image adjustments"), elem_classes=["bp-label-block"])
                with gr.Row():
                    with gr.Column(scale=1):
                        live_preview = gr.Image(
                            label="Preview — applies to all images",
                            interactive=False,
                            height=420,
                        )
                    with gr.Column(scale=1):
                        brightness_slider = gr.Slider(
                            minimum=0.5, maximum=1.5, value=1.0, step=0.05, label="Brightness"
                        )
                        contrast_slider = gr.Slider(
                            minimum=0.5, maximum=1.5, value=1.0, step=0.05, label="Contrast"
                        )
                        saturation_slider = gr.Slider(
                            minimum=0.5, maximum=1.5, value=1.0, step=0.05, label="Saturation"
                        )
                        sharpness_slider = gr.Slider(
                            minimum=0.5, maximum=2.0, value=1.0, step=0.05, label="Sharpness"
                        )
                        reset_btn = gr.Button("Reset to defaults", size="sm")

                run_btn = gr.Button("Process batch", variant="primary", size="lg")

        # ── Status ─────────────────────────────────────────────────────────
        status_out = gr.HTML(value="", visible=False, elem_classes=["bp-status-block"])

        # ── Results zone ───────────────────────────────────────────────────
        _divider = (
            f'<div class="bp-results-divider">'
            f'<div class="bp-divider-line"></div>'
            f'<div class="bp-divider-label">{_ICO_RESULTS}Results</div>'
            f'<div class="bp-divider-line"></div>'
            f'</div>'
        )
        with gr.Row(visible=False, elem_classes=["bp-label-block"]) as results_header_row:
            gr.HTML(_divider)

        with gr.Row(visible=False) as preview_row:
            before_gal = gr.Gallery(
                label="Original", columns=4, object_fit="contain", height="auto"
            )
            after_gal = gr.Gallery(
                label="Processed", columns=4, object_fit="contain", height="auto"
            )

        # ── Download zone ──────────────────────────────────────────────────
        with gr.Row(visible=False, elem_classes=["bp-label-block"]) as download_header_row:
            gr.HTML(_label(_ICO_DOWNLOAD, "Download"))

        with gr.Row(visible=False) as download_row:
            with gr.Column():
                individual_out = gr.File(label="Individual images", file_count="multiple")
            with gr.Column():
                zip_out = gr.File(label="Full batch ZIP")

        # ── Event wiring ───────────────────────────────────────────────────

        # Outputs shared by upload + clear handlers
        _upload_outs = [
            accumulated_files, bgremoved_state, centered_state,
            live_preview, status_out,
            file_input,          # reset to empty drop zone after each add
            queue_gallery,
        ]

        def _on_upload(new_files, existing, bgr_cache, cen_cache, canvas_w, canvas_h):
            old_first = existing[0] if existing else None
            existing = list(existing or [])
            seen = set(existing)
            for f in (new_files or []):
                if f not in seen:
                    existing.append(f)
                    seen.add(f)
            gallery, existing = _files_to_gallery(existing)
            # Skip rembg when the first file hasn't changed
            new_first = existing[0] if existing else None
            if new_first != old_first:
                bgr, cen, prev, st = _prepare_cache(existing, canvas_w, canvas_h)
            else:
                bgr, cen = bgr_cache, cen_cache
                prev = _preview_on_white(cen) if cen else None
                st = gr.update(value="", visible=False)
            return (
                existing, bgr, cen, prev, st,
                gr.update(value=None),                          # reset file_input → drop zone
                gr.update(value=gallery, visible=bool(gallery)),
            )

        def _on_clear():
            return (
                [], None, None, None,
                gr.update(value="", visible=False),
                gr.update(value=None),
                gr.update(value=[], visible=False),
            )

        def _on_gallery_delete(evt: gr.EventData, files, bgr_cache, cen_cache, canvas_w, canvas_h):
            # Note: uses the base EventData type (not gr.DeletedFileData) —
            # Gradio 6.19's DeletedFileData constructor crashes because the
            # frontend payload is {file, index} but FileData(**data) expects
            # a flat file dict. evt.index still resolves via EventData's
            # dict-backed __getattr__ — guarded with getattr() since a future
            # Gradio version could drop the key entirely (__getattr__ raises
            # AttributeError, not None, on a missing key).
            files = list(files or [])
            idx = getattr(evt, "index", None)
            removed_first = idx == 0
            if idx is not None and 0 <= idx < len(files):
                files.pop(idx)
            gallery, files = _files_to_gallery(files)
            gallery_update = gr.update(value=gallery, visible=bool(gallery))
            if not removed_first:
                # Preview cache still reflects files[0], which hasn't moved.
                return files, bgr_cache, cen_cache, gr.update(), gr.update(), gallery_update
            bgr, cen, prev, st = _prepare_cache(files, canvas_w, canvas_h)
            return files, bgr, cen, prev, st, gallery_update

        file_input.upload(
            fn=_on_upload,
            inputs=[file_input, accumulated_files, bgremoved_state, centered_state,
                    width_in, height_in],
            outputs=_upload_outs,
        )
        file_input.clear(fn=_on_clear, outputs=_upload_outs)

        queue_gallery.delete(
            fn=_on_gallery_delete,
            inputs=[accumulated_files, bgremoved_state, centered_state,
                    width_in, height_in],
            outputs=[accumulated_files, bgremoved_state, centered_state,
                     live_preview, status_out, queue_gallery],
        )

        for component in [width_in, height_in]:
            component.change(
                fn=_recenter_preview,
                inputs=[bgremoved_state, width_in, height_in],
                outputs=[centered_state, live_preview],
            )

        adj_inputs = [centered_state, brightness_slider, contrast_slider, saturation_slider, sharpness_slider]
        for slider in [brightness_slider, contrast_slider, saturation_slider, sharpness_slider]:
            slider.release(fn=_enhance_preview, inputs=adj_inputs, outputs=[live_preview])

        reset_btn.click(
            fn=lambda c: (1.0, 1.0, 1.0, 1.0, _preview_on_white(c) if c is not None else None),
            inputs=[centered_state],
            outputs=[brightness_slider, contrast_slider, saturation_slider, sharpness_slider, live_preview],
        )

        def run(
            files, width, height, fmt,
            brightness, contrast, saturation, sharpness,
            progress=gr.Progress(),
        ):
            zip_p, raw_status, before, after, individuals = process_batch(
                files, width, height, fmt,
                brightness, contrast, saturation, sharpness,
                progress,
            )
            has_results = bool(before)
            return (
                zip_p,
                gr.update(value=_status_html(raw_status, has_results), visible=True),
                before,
                after,
                individuals,
                gr.update(visible=has_results),
                gr.update(visible=has_results),
                gr.update(visible=has_results),
                gr.update(visible=has_results),
            )

        run_btn.click(
            fn=run,
            inputs=[
                accumulated_files, width_in, height_in, fmt_radio,
                brightness_slider, contrast_slider, saturation_slider, sharpness_slider,
            ],
            outputs=[
                zip_out,
                status_out,
                before_gal,
                after_gal,
                individual_out,
                results_header_row,
                preview_row,
                download_header_row,
                download_row,
            ],
        )

    return demo


def main() -> None:
    _build_ui().launch(
        inbrowser=True,
        theme=_THEME,
        css=_CSS,
        js=_INIT_JS,
    )


if __name__ == "__main__":
    main()
