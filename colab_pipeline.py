import os
import subprocess
from pathlib import Path
from typing import List, Optional

from docling import DocumentConverter
from docling.pdf import PdfPipelineOptions
from docling.ocr import TesseractOcrOptions

from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageEnhance
import img2pdf
import mimetypes
import zipfile


def install_system_deps():
    """Install necessary system packages using apt."""
    packages = [
        "poppler-utils", "tesseract-ocr", "libtesseract-dev", "pkg-config",
        "libpoppler-cpp-dev", "poppler-data", "ffmpeg"
    ]
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt-get", "install", "-y"] + packages, check=True)


def install_python_deps():
    """Install python dependencies using pip."""
    packages = [
        "docling[complete]", "paddleocr", "pdf2image", "img2pdf", "gradio"
    ]
    subprocess.run(["pip", "install", "-U"] + packages, check=True)


# Image preprocessing helpers -------------------------------------------------

def enhance_image(img: Image.Image) -> Image.Image:
    """Improve image quality with contrast and sharpening."""
    img_gray = img.convert("L")
    img_filtered = img_gray.filter(ImageFilter.MedianFilter(size=3))
    enhancer = ImageEnhance.Contrast(img_filtered)
    img_contrasted = enhancer.enhance(2.0)
    img_sharp = img_contrasted.filter(
        ImageFilter.UnsharpMask(radius=1, percent=150)
    )
    return img_sharp


def preprocess_pdf(src_path: str, dst_path: str) -> None:
    """Convert each page of a PDF to an enhanced image and rebuild PDF."""
    pages = convert_from_path(src_path)
    enhanced_paths: List[str] = []
    tmp_dir = Path(dst_path).with_suffix("").name + "_pages"
    tmp_dir = Path("/tmp") / tmp_dir
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for i, page in enumerate(pages):
        out_img = enhance_image(page)
        img_path = tmp_dir / f"page_{i:04d}.png"
        out_img.save(img_path, "PNG")
        enhanced_paths.append(str(img_path))

    with open(dst_path, "wb") as f_out:
        f_out.write(img2pdf.convert(enhanced_paths))

# -----------------------------------------------------------------------------


def detect_file_type(path: str) -> str:
    """Guess file type using mimetypes or extension."""
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type:
        return mime_type
    return Path(path).suffix


def setup_converter() -> DocumentConverter:
    """Create a Docling converter configured for OCR."""
    tesseract_opts = TesseractOcrOptions(languages=["por", "eng"], do_ocr=True)
    pdf_opts = PdfPipelineOptions(ocr_options=tesseract_opts)
    return DocumentConverter(pdf=pdf_opts)


def convert_document(
    file_path: str,
    output_format: str = "markdown",
    ocr_engine: str = "tesseract",
) -> str:
    """Convert a document to the desired format with optional OCR engine."""
    file_type = detect_file_type(file_path)

    # Temporary: preprocess low-quality PDF images before conversion
    processed_path = file_path
    if file_type == "application/pdf":
        processed_path = str(Path(file_path).with_suffix(".clean.pdf"))
        preprocess_pdf(file_path, processed_path)

    converter = setup_converter()
    result_path = str(Path(file_path).with_suffix("." + output_format))
    converter.convert(processed_path, result_path, output_format)
    return result_path


def process_multiple_files(
    files: List[str],
    output_format: str = "markdown",
    create_zip: bool = False,
) -> Optional[str]:
    """Process a list of documents, optionally zip the results."""
    output_dir = Path("/content/converted_docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for file in files:
        out = convert_document(file, output_format=output_format)
        dst = output_dir / Path(out).name
        os.replace(out, dst)
        results.append(str(dst))

    if create_zip:
        zip_path = output_dir / "converted.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in results:
                zf.write(f, Path(f).name)
        return str(zip_path)
    return None


if __name__ == "__main__":
    # Example usage: convert a single file
    pass
