import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List


class CSVParser:
    def process_document(self, csv_path: str) -> List[Dict]:
        """Parse the CSV file for RAG processing."""
        path = Path(csv_path)
        chunks = []

        with open(path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader):
                parts = []
                for key, value in row.items():
                    if value:
                        parts.append(f"{key}: {value}")

                chunks.append(
                    {
                        "id": self._generate_doc_id(str(path)),
                        "text": " | ".join(parts),
                        "metadata": {
                            "source": str(path),
                            "row_number": idx,
                            **row,
                        },
                    }
                )

        return chunks

    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique document ID based on file path."""
        return hashlib.md5(file_path.encode()).hexdigest()


if __name__ == "__main__":
    parser = CSVParser()
    chunks = parser.process_document("./data/sample.csv")

    if chunks:
        print("\nSample chunk:")
        print(json.dumps(chunks[574], indent=2))
        print(f"\nTotal Chunks: {len(chunks)}")
