import hashlib
from pathlib import Path

from docx import Document


class DocxParser:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, file_path: str) -> list[dict]:
        """parse docx and create chunks"""
        doc_data = self._parse_docx(file_path)
        chunks = self._chunk_text(doc_data["content"])

        for chunk in chunks:
            chunk["document_metadata"] = doc_data["metadata"]

        return chunks

    def _parse_docx(self, file_path: str) -> dict:
        """Parse a docx file and extract content with metadata."""
        path = Path(file_path)
        doc = Document(file_path)

        paragraphs = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                paragraphs.append(text)

        content = "\n\n".join(paragraphs)
        core_props = doc.core_properties

        metadata = {
            "filename": path.name,
            "file_path": str(path.absolute()),
            "title": core_props.title or "Untitled",
            "author": core_props.author or "Unknown",
            "created": str(core_props.created) if core_props.created else None,
            "modified": str(core_props.modified) if core_props.modified else None,
        }

        return {"content": content, "metadata": metadata}

    def _chunk_text(self, text: str) -> list[dict]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size

            if end < len(text):
                for i in range(end, max(start + self.chunk_size - 200, start), -1):
                    if i < len(text) and text[i : i + 2] == "\n\n":
                        end = i + 2
                        break
                else:
                    sentence_ends = [".", "!", "?"]
                    for i in range(end, max(start + self.chunk_size - 100, start), -1):
                        if i < len(text) and text[i] in sentence_ends:
                            end = i + 1
                            break
                    else:
                        for i in range(
                            end, max(start + self.chunk_size - 50, start), -1
                        ):
                            if i < len(text) and text[i].isspace():
                                end = i
                                break

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "start_char": start,
                        "end_char": end,
                        "chunk_length": len(chunk_text),
                    }
                )
                chunk_id += 1

            if end < len(text):
                start = end - self.chunk_overlap
            else:
                start = end

        return chunks

    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique document ID."""
        return hashlib.md5(file_path.encode()).hexdigest()


if __name__ == "__main__":
    parser = DocxParser()
    chunks = parser.process_document("./data/sample.docx")

    for chunk in chunks:
        print(f"--- Chunk {chunk['chunk_id']} (Length: {chunk['chunk_length']}) ---")
        print(chunk["text"])
        print("----------------------------------------------------------------\n")
