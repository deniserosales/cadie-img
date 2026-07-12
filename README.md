# cadie-img

Standalone image processing tool for Cadie Handmade product photos. Removes
the background, centers the piece on a 1080×1080 canvas, and exports as WebP
or PNG — individually or as a batch.

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
2. **Adjust controls** — canvas size, output format (WebP/PNG), and image
   adjustments (brightness, contrast, saturation, sharpness) with a live
   preview.
3. **Process batch** — runs background removal and centering on every queued
   image, then download the results individually or as a single ZIP.

## Architecture

`app.py` is the Gradio entry point — it builds the UI and wires upload,
preview, and batch-processing events. Image processing is split into
single-purpose modules under `core/`:

- `background_remover.py` — removes the background via `rembg` and cleans up
  alpha-mask edges.
- `composer.py` — crops to content and centers the piece on a padded,
  transparent canvas.
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
