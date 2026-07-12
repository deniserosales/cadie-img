# cadie-img

Standalone image processing tool for Cadie Handmade product photos. Detects
the piece with `rembg`, reframes it on a 1080×1080 square using its
*original* background (never removed or replaced), and exports as WebP or
PNG — individually or as a batch.

## Requirements

- Python 3.9+
- macOS or Linux (Apple Silicon compatible)
- Key dependencies: `rembg[cpu]`, `Pillow`, `gradio`

## Installation

```
git clone git@github.com:deniserosales/cadie-img.git
cd cadie-img
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

With the virtualenv active, run:

```
cadie-img
```

This opens the interface in your browser. The flow is:

1. **Upload images** — drop or select one or more product photos; they queue
   up as thumbnails.
2. **Adjust controls** — output format (WebP/PNG) and image adjustments
   (brightness, contrast, saturation, sharpness) with a live preview.
3. **Process batch** — reframes every queued image on its own original
   background, then download the results individually or as a single ZIP.

## Architecture

`app.py` is the Gradio entry point — it builds the UI and wires upload,
preview, and batch-processing events. Image processing is split into
single-purpose modules under `core/`:

- `background_remover.py` — runs `rembg` purely to locate the piece and
  returns the bounding box of its alpha mask; the segmentation cutout
  itself is discarded.
- `composer.py` — crops the *original* photo to a square region around
  that bounding box with a `PADDING_RATIO` margin, then resizes to
  1080×1080. The photo's real background is preserved untouched.
- `resizer.py` — resizes an image to target dimensions, with or without
  preserving aspect ratio.
- `enhancer.py` — applies brightness/contrast/saturation/sharpness
  adjustments.
- `zipper.py` — packs processed images into a downloadable ZIP archive.
- `presets.py` — visual style constants (padding ratio, WebP
  quality/method) shared by the pipeline above.

## Project context

Internal tool for processing Cadie Handmade (wire-wrap jewelry) product
images before uploading them to the site.
