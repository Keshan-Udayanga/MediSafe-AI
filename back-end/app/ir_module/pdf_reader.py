import fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF binary data using PyMuPDF.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    # Iterate through each page in the PDF and extract text
    for page in document:
        text = page.get_text()

        if text:
            # Append the extracted text to the pages list
            pages.append(text)

    document.close()

    # Return the extracted text from all pages as a single string, separated by newlines
    return "\n".join(pages)