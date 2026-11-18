"""Leitura de documentos de suporte (.md e .txt) do disco."""

import hashlib
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = frozenset({".md", ".markdown", ".txt"})


class UnsupportedDocumentError(ValueError):
    """Arquivo com extensão não suportada."""


@dataclass(frozen=True)
class Document:
    doc_id: str
    source: str
    text: str
    content_hash: str

    @property
    def is_markdown(self) -> bool:
        return Path(self.source).suffix.lower() in {".md", ".markdown"}


def make_doc_id(source: str) -> str:
    """Id estável derivado do nome do arquivo: reingerir o mesmo arquivo gera o mesmo id."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def document_from_text(source: str, text: str) -> Document:
    suffix = Path(source).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(f"Extensão não suportada: {suffix or '(sem extensão)'}")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return Document(
        doc_id=make_doc_id(source),
        source=source,
        text=normalized,
        content_hash=hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
    )


def load_document(path: Path) -> Document:
    return document_from_text(path.name, path.read_text(encoding="utf-8"))


def load_directory(directory: Path) -> list[Document]:
    """Carrega todos os arquivos suportados da pasta (recursivo), em ordem alfabética."""
    paths = sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return [
        document_from_text(p.relative_to(directory).as_posix(), p.read_text(encoding="utf-8"))
        for p in paths
    ]
