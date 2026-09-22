import os

import pdfplumber
from docx import Document


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF resume.

    Uses pdfplumber to read each page and
    clean common PDF extraction artifacts.
    """

    text = ""

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                # Fix common PDF bullet extraction artifact
                page_text = page_text.replace(
                    "(cid:127)",
                    "•"
                )

                # Fix other common PDF extraction artifacts
                page_text = page_text.replace(
                    "\x7f",
                    "•"
                )

                text += page_text + "\n"

    return text.strip()


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX resume.

    Reads all non-empty paragraphs.
    """

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:

        paragraph_text = paragraph.text.strip()

        if paragraph_text:
            text.append(paragraph_text)

    return "\n".join(text).strip()


def extract_resume_text(file_path):
    """
    Detect the resume file type and extract its text.

    Supported formats:
    - PDF
    - DOCX
    """

    # Check whether the file exists
    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    # Get file extension
    extension = os.path.splitext(
        file_path
    )[1].lower()

    # PDF
    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    # DOCX
    elif extension == ".docx":

        return extract_text_from_docx(
            file_path
        )

    # Unsupported file
    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload a PDF or DOCX resume."
        )