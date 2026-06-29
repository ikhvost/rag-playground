from pathlib import Path

import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFParser:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def process_document(self, pdf_path: str) -> list[dict]:
        """Parse a PDF and return chunked text with metadata."""
        text = self._extract_text_from_pdf(pdf_path)
        chunks = self._chunk_text(text)
        results = []

        for idx, chunk in enumerate(chunks):
            results.append(
                {
                    "chunk_id": idx,
                    "text": chunk,
                    "source": pdf_path,
                    "chunk_length": len(chunk),
                    "total_chunks": len(chunks),
                }
            )

        return results

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = fitz.open(str(path))
            text = "\n\n".join(str(page.get_text()) for page in doc)
            doc.close()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}") from e

        return text

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into chunks."""
        chunks = self.text_splitter.split_text(text)
        return chunks


if __name__ == "__main__":
    parser = PDFParser()
    chunks = parser.process_document("./data/sample.pdf")

    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_id']}:")
        print(f"Length: {chunk['chunk_length']} chars")
        print(f"Text: {chunk['text']}")
