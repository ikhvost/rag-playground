import hashlib
from pathlib import Path
from typing import Dict, List


class TextDocumentParser:
    """Parse text files for RAG system ingestion."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, file_path: str) -> List[Dict]:
        """Parse file and create chunks."""
        data = self._parse_file(file_path)
        chunks = self._chunk_text(data["content"])

        for chunk in chunks:
            chunk["document_metadata"] = data["metadata"]
        return chunks

    def _parse_file(self, file_path: str) -> Dict:
        """Parse a text file and extract content with metadata."""
        path = Path(file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        metadata = {
            "filename": path.name,
            "file_path": str(path.absolute()),
            "file_size": path.stat().st_size,
            "file_extension": path.suffix,
            "document_id": self._generate_doc_id(file_path),
            "char_count": len(content),
            "word_count": len(content.split()),
        }

        return {"content": content, "metadata": metadata}

    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique document ID based on file path."""
        return hashlib.md5(file_path.encode()).hexdigest()

    def _chunk_text(self, text: str) -> List[Dict]:
        """Split text into overlapping chunks for RAG processing."""
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size

            if end < len(text):
                sentence_ends = [".", "!", "?", "\n\n"]
                best_break = end

                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if i < len(text) and text[i] in sentence_ends:
                        best_break = i + 1
                        break

                if best_break == end:
                    for i in range(end, max(start + self.chunk_size - 50, start), -1):
                        if i < len(text) and text[i].isspace():
                            best_break = i
                            break

                end = best_break

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


if __name__ == "__main__":
    parser = TextDocumentParser(chunk_size=500, chunk_overlap=100)
    chunks = parser.process_document("./data/sample.txt")

    print(f"Document: {chunks[0]['document_metadata']['filename']}")
    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_id']}:")
        print(f"Length: {chunk['chunk_length']} chars")
        print(f"Text: {chunk['text']}")
