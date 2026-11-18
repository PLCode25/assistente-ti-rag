from pathlib import Path

import pytest

from app.rag.chunking import chunk_document, split_sections, split_text
from app.rag.documents import document_from_text, load_directory

SAMPLE_DOCS = Path(__file__).resolve().parents[2] / "docs-exemplo"

LOREM = " ".join(f"palavra{i}" for i in range(400))  # ~4 mil caracteres, sem quebras de linha


# --- split_text -------------------------------------------------------------


def test_short_text_is_single_chunk() -> None:
    assert split_text("  texto curto  ", chunk_size=100, chunk_overlap=10) == ["texto curto"]


def test_empty_text_has_no_chunks() -> None:
    assert split_text("   \n  ", chunk_size=100, chunk_overlap=10) == []


def test_chunks_respect_max_size() -> None:
    chunks = split_text(LOREM, chunk_size=200, chunk_overlap=40)

    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_chunks_cover_all_words_in_order() -> None:
    chunks = split_text(LOREM, chunk_size=200, chunk_overlap=40)
    words_seen: list[str] = []
    for chunk in chunks:
        for word in chunk.split():
            if not words_seen or word not in words_seen[-20:]:
                words_seen.append(word)

    assert words_seen == LOREM.split()


def test_consecutive_chunks_overlap() -> None:
    chunks = split_text(LOREM, chunk_size=200, chunk_overlap=40)

    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        first_word = nxt.split()[0]
        assert first_word in prev.split(), "o próximo trecho deve começar dentro do anterior"


def test_chunks_do_not_start_mid_word() -> None:
    chunks = split_text(LOREM, chunk_size=200, chunk_overlap=40)
    words = set(LOREM.split())

    assert all(c.split()[0] in words for c in chunks)
    assert all(c.split()[-1] in words for c in chunks)


def test_prefers_paragraph_breaks() -> None:
    para1 = "Primeiro parágrafo. " * 6  # ~120 caracteres
    para2 = "Segundo parágrafo. " * 6
    chunks = split_text(f"{para1}\n\n{para2}", chunk_size=180, chunk_overlap=0)

    assert chunks[0] == para1.strip()
    assert chunks[1] == para2.strip()


def test_word_longer_than_chunk_is_hard_split() -> None:
    chunks = split_text("x" * 250, chunk_size=100, chunk_overlap=0)
    assert [len(c) for c in chunks] == [100, 100, 50]


@pytest.mark.parametrize(("size", "overlap"), [(0, 0), (100, 100), (100, -1)])
def test_invalid_parameters(size: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        split_text("abc", chunk_size=size, chunk_overlap=overlap)


# --- split_sections ---------------------------------------------------------


def test_split_sections_tracks_headings() -> None:
    text = "Intro solta.\n# Título\nCorpo 1.\n## Sub\nCorpo 2.\n### Vazia\n"

    assert split_sections(text) == [
        (None, "Intro solta."),
        ("Título", "Corpo 1."),
        ("Sub", "Corpo 2."),
    ]


def test_hash_inside_text_is_not_heading() -> None:
    assert split_sections("Use a tag #suporte\n#semespaço") == [
        (None, "Use a tag #suporte\n#semespaço")
    ]


# --- chunk_document ---------------------------------------------------------


def test_markdown_chunks_carry_section_and_metadata() -> None:
    doc = document_from_text("vpn.md", "# VPN\nTexto geral.\n## Erro de login\nVerifique a senha.")

    chunks = chunk_document(doc, chunk_size=800, chunk_overlap=100)

    assert [(c.section, c.text) for c in chunks] == [
        ("VPN", "Texto geral."),
        ("Erro de login", "Verifique a senha."),
    ]
    assert chunks[1].metadata == {
        "doc_id": doc.doc_id,
        "source": "vpn.md",
        "chunk_index": 1,
        "section": "Erro de login",
    }


def test_txt_is_not_split_by_headings() -> None:
    doc = document_from_text("notas.txt", "# não é título\nconteúdo")

    chunks = chunk_document(doc, chunk_size=800, chunk_overlap=100)

    assert len(chunks) == 1
    assert chunks[0].section is None
    assert "section" not in chunks[0].metadata


def test_chunk_ids_are_deterministic_and_unique() -> None:
    doc = document_from_text("longo.txt", LOREM)

    first = chunk_document(doc, chunk_size=200, chunk_overlap=40)
    second = chunk_document(doc, chunk_size=200, chunk_overlap=40)

    assert [c.id for c in first] == [c.id for c in second]
    assert len({c.id for c in first}) == len(first)
    assert [c.chunk_index for c in first] == list(range(len(first)))
    assert first[0].id == f"{doc.doc_id}:0"


def test_sample_docs_chunk_within_limits() -> None:
    for doc in load_directory(SAMPLE_DOCS):
        chunks = chunk_document(doc, chunk_size=800, chunk_overlap=150)
        assert chunks, doc.source
        assert all(0 < len(c.text) <= 800 for c in chunks)
