from pathlib import Path

import pytest

from app.rag.documents import (
    UnsupportedDocumentError,
    document_from_text,
    load_directory,
    load_document,
    make_doc_id,
)

SAMPLE_DOCS = Path(__file__).resolve().parents[2] / "docs-exemplo"


def test_doc_id_is_stable_for_same_source() -> None:
    assert make_doc_id("vpn.md") == make_doc_id("vpn.md")
    assert make_doc_id("vpn.md") != make_doc_id("senha.md")


def test_content_change_keeps_doc_id_but_changes_hash() -> None:
    v1 = document_from_text("vpn.md", "versão 1")
    v2 = document_from_text("vpn.md", "versão 2")

    assert v1.doc_id == v2.doc_id
    assert v1.content_hash != v2.content_hash


def test_normalizes_line_endings() -> None:
    doc = document_from_text("a.txt", "linha 1\r\nlinha 2\rlinha 3")
    assert doc.text == "linha 1\nlinha 2\nlinha 3"


@pytest.mark.parametrize("name", ["planilha.xlsx", "sem_extensao"])
def test_rejects_unsupported_extensions(name: str) -> None:
    with pytest.raises(UnsupportedDocumentError):
        document_from_text(name, "conteúdo")


def test_load_document_reads_utf8(tmp_path: Path) -> None:
    path = tmp_path / "acentos.md"
    path.write_text("# Configuração\nAção não é opção.", encoding="utf-8")

    doc = load_document(path)

    assert doc.source == "acentos.md"
    assert "Ação não é opção." in doc.text
    assert doc.is_markdown


def test_load_directory_is_recursive_sorted_and_skips_unsupported(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "b.md").write_text("B", encoding="utf-8")
    (tmp_path / "a.txt").write_text("A", encoding="utf-8")
    (tmp_path / "sub" / "c.md").write_text("C", encoding="utf-8")
    (tmp_path / "ignorar.pdf").write_bytes(b"%PDF")

    docs = load_directory(tmp_path)

    assert [d.source for d in docs] == ["a.txt", "b.md", "sub/c.md"]


def test_sample_docs_load() -> None:
    docs = load_directory(SAMPLE_DOCS)
    assert {d.source for d in docs} == {"impressora.txt", "senha.md", "vpn.md"}
