import unittest

from app import chunk_preview, score_documents, DocumentChunk


class AppTests(unittest.TestCase):
    def test_score_documents_orders_by_overlap(self) -> None:
        docs = [
            DocumentChunk(source="a.md", text="alpha beta"),
            DocumentChunk(source="b.md", text="gamma delta"),
        ]
        ranked = score_documents("alpha", docs)
        self.assertEqual(ranked[0][0].source, "a.md")

    def test_chunk_preview_compacts_whitespace(self) -> None:
        self.assertEqual(chunk_preview("a\n\nb"), "a b")


if __name__ == "__main__":
    unittest.main()
