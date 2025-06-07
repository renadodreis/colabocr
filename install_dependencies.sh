#!/bin/bash
# Install all system and Python dependencies for the Docling OCR pipeline.
set -e

# System packages required for OCR and PDF processing
apt-get update
apt-get install -y \
    poppler-utils tesseract-ocr libtesseract-dev pkg-config \
    libpoppler-cpp-dev poppler-data ffmpeg

# Python dependencies used by colab_pipeline.py
pip install -U \
    docling[complete] paddleocr pdf2image img2pdf gradio
