"""Divisão de documentos em trechos (chunks) com sobreposição e metadados."""

import re
from dataclasses import dataclass

from app.rag.documents import Document

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    source: str
    section: str | None
    chunk_index: int
    text: str

    @property
    def metadata(self) -> dict[str, str | int]:
        meta: dict[str, str | int] = {
            "doc_id": self.doc_id,
            "source": self.source,
            "chunk_index": self.chunk_index,
        }
        if self.section:
            meta["section"] = self.section
        return meta


def split_sections(text: str) -> list[tuple[str | None, str]]:
    """Separa Markdown em pares (título da seção, corpo).

    O texto antes do primeiro título fica com seção None; seções sem corpo são descartadas.
    """
    sections: list[tuple[str | None, list[str]]] = [(None, [])]
    for line in text.split("\n"):
        match = _HEADING_RE.match(line)
        if match:
            sections.append((match.group(2), []))
        else:
            sections[-1][1].append(line)
    bodies = [(title, "\n".join(lines).strip()) for title, lines in sections]
    return [(title, body) for title, body in bodies if body]


def _find_break(text: str, start: int, end: int) -> int:
    """Melhor ponto de quebra em text[start:end]: parágrafo > linha > frase > palavra."""
    min_pos = start + (end - start) // 2
    for sep in ("\n\n", "\n", ". ", "? ", "! ", "; ", " "):
        pos = text.rfind(sep, min_pos, end)
        if pos != -1:
            return pos + len(sep)
    return end


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Divide o texto em pedaços de até `chunk_size` caracteres, sobrepostos em `chunk_overlap`."""
    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser positivo")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap deve estar entre 0 e chunk_size - 1")

    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            end = _find_break(text, start, end)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break

        next_start = max(end - chunk_overlap, start + 1)
        # Evita começar o próximo trecho no meio de uma palavra.
        if next_start < end and not text[next_start - 1].isspace():
            space = text.find(" ", next_start, end)
            next_start = space + 1 if space != -1 else next_start
        start = next_start
    return chunks


def chunk_document(document: Document, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    sections = split_sections(document.text) if document.is_markdown else [(None, document.text)]
    chunks: list[Chunk] = []
    for section, body in sections:
        for piece in split_text(body, chunk_size, chunk_overlap):
            index = len(chunks)
            chunks.append(
                Chunk(
                    id=f"{document.doc_id}:{index}",
                    doc_id=document.doc_id,
                    source=document.source,
                    section=section,
                    chunk_index=index,
                    text=piece,
                )
            )
    return chunks
