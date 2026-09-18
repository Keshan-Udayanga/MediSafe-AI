import fitz


def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text().strip()
            if text:
                pages.append({"page_number": page_number, "text": text})
    finally:
        document.close()
    return pages