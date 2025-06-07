# Docling OCR Pipeline for Colab

This repository contains a Python script to convert PDF documents using
[Docling](https://github.com/docling-project/docling) with enhanced OCR
processing. The focus is on high‑quality text extraction from low-resolution
PDFs.

## Features

- Automatic installation of required system packages and Python
  dependencies (Docling, Tesseract, etc.)
- Image preprocessing to improve OCR accuracy on poorly scanned pages
- Conversion to multiple formats: Markdown, JSON, HTML or TXT
- Batch processing with optional ZIP export

## Usage

Run the script in Google Colab:

```python
!python colab_pipeline.py
```

## Installing Dependencies

If you prefer to install all requirements manually before running the
pipeline, execute the helper script:

```bash
!bash install_dependencies.sh
```

Create your own workflow or interface (e.g. with Gradio) using the helper
functions defined in `colab_pipeline.py`.
