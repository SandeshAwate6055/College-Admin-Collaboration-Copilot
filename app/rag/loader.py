import fitz  # PyMuPDF
import os

def load_pdfs(pdf_folder: str = "data/pdfs") -> list[dict]:
    """
    Returns a list of dicts:
    { "text": "...", "source": "fees_rules.pdf", "page": 3 }
    """
    documents = []
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_folder, filename)
            doc = fitz.open(path)
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text().strip()
                if text:  # skip blank pages
                    documents.append({
                        "text": text,
                        "source": filename,
                        "page": page_num
                    })
    return documents
