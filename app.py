#!/usr/bin/env python3
"""MCP demo server and CLI."""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from openai import OpenAI

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - test environments may not install mcp yet
    FastMCP = None


load_dotenv()

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
DEFAULT_MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
DEFAULT_MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")


@dataclass(frozen=True)
class DocumentChunk:
    source: str
    text: str


def load_documents(docs_dir: Path = DOCS_DIR) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(docs_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            chunks.append(DocumentChunk(source=str(path.relative_to(ROOT)), text=text))
    return chunks


def score_documents(question: str, documents: Iterable[DocumentChunk]) -> list[tuple[DocumentChunk, int]]:
    question_words = {word.lower().strip(".,:;!?") for word in question.split() if word}
    scored: list[tuple[DocumentChunk, int]] = []
    for document in documents:
        tokens = {word.lower().strip(".,:;!?") for word in document.text.split() if word}
        overlap = len(question_words & tokens)
        scored.append((document, overlap))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored


def chunk_preview(text: str, limit: int = 300) -> str:
    compact = " ".join(text.split())
    return compact[:limit]


def build_answer(question: str, top_documents: list[DocumentChunk]) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI()
    context = "\n\n".join(f"[{index + 1}] {doc.source}\n{doc.text}" for index, doc in enumerate(top_documents))
    prompt = (
        "Answer the question using only the provided context when possible. "
        "If the context is insufficient, say so plainly.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{context}"
    )
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "Use the supplied context and keep the answer concise."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def list_documents() -> str:
    documents = load_documents()
    if not documents:
        return "No documents found."
    lines = []
    for doc in documents:
        lines.append(f"{doc.source}\n{chunk_preview(doc.text)}")
    return "\n\n".join(lines)


def search_documents(question: str, limit: int = 3) -> str:
    documents = load_documents()
    scored = score_documents(question, documents)[:limit]
    if not scored:
        return "No documents found."
    lines = []
    for document, score in scored:
        lines.append(f"{document.source} | score={score}")
        lines.append(chunk_preview(document.text))
    return "\n\n".join(lines)


def summarize_documents() -> str:
    documents = load_documents()
    if not documents:
        return "No documents found."
    return "\n".join(f"- {doc.source}: {chunk_preview(doc.text, 180)}" for doc in documents)


def run_cli(question: str) -> None:
    documents = load_documents()
    scored = score_documents(question, documents)
    top_documents = [doc for doc, _ in scored[:3]]
    print("\nRetrieved:\n")
    for doc, score in scored[:3]:
        print(f"- {doc.source} | score={score}")
    print("\nAnswer:\n")
    print(build_answer(question, top_documents))


def build_mcp_server(host: str = DEFAULT_MCP_HOST, port: int = DEFAULT_MCP_PORT):
    if FastMCP is None:
        raise RuntimeError("mcp is not installed.")

    server = FastMCP("LangChain MCP Demo", host=host, port=port)

    @server.tool()
    def list_docs() -> str:
        return list_documents()

    @server.tool()
    def search_docs(query: str) -> str:
        return search_documents(query)

    @server.tool()
    def summarize_docs() -> str:
        return summarize_documents()

    return server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MCP demo server and grounded CLI")
    parser.add_argument("question", nargs="?", help="Ask a question in CLI mode")
    parser.add_argument("--cli", action="store_true", help="Run as a CLI instead of MCP stdio server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http", "sse"),
        default=DEFAULT_MCP_TRANSPORT,
        help="Transport to use when running as an MCP server",
    )
    parser.add_argument("--host", default=DEFAULT_MCP_HOST, help="Host for HTTP transports")
    parser.add_argument("--port", type=int, default=DEFAULT_MCP_PORT, help="Port for HTTP transports")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.cli:
        question = args.question or input("Question: ").strip()
        if not question:
            print("A question is required.")
            return 1
        run_cli(question)
        return 0

    server = build_mcp_server(host=args.host, port=args.port)
    server.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
