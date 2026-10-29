from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.core.config import Settings
from app.models.document import DocumentStatus
from app.rag.generation import GeneratedAnswer
from app.rag.provider_factory import embedding_space_for_provider
from app.rag.service import QuestionAnsweringService
from app.rag.types import RetrievedChunk


class FakeSession:
    async def commit(self) -> None:
        return None


class FakeEmbeddingProvider:
    dimensions = 3
    provider_name = "citation-test"
    model = "citation-test-model"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0, 0.0, 0.0] for _ in texts]


class FakeDocuments:
    def __init__(self, document: SimpleNamespace) -> None:
        self.document = document

    async def get(self, document_id: UUID) -> SimpleNamespace | None:
        return self.document if document_id == self.document.id else None


class FakeRetriever:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self.chunks = chunks

    async def retrieve(self, **_kwargs: object) -> list[RetrievedChunk]:
        return self.chunks


class FakeEvents:
    async def create(self, **_kwargs: object) -> None:
        return None


class StubAnswerProvider:
    model_name = "citation-test-provider"

    def __init__(self, generated: GeneratedAnswer) -> None:
        self.generated = generated

    async def answer(
        self, *, question: str, context: list[RetrievedChunk]
    ) -> GeneratedAnswer:
        del question, context
        return self.generated


def make_service(generated: GeneratedAnswer) -> tuple[QuestionAnsweringService, UUID, UUID, UUID]:
    document_id = uuid4()
    first_chunk_id = uuid4()
    second_chunk_id = uuid4()
    embedding_provider = FakeEmbeddingProvider()
    chunks = [
        RetrievedChunk(
            chunk_id=first_chunk_id,
            document_id=document_id,
            chunk_index=0,
            content="The interview loop has three stages.",
            heading_path=["Interview process"],
            page_start=1,
            page_end=1,
            score=0.95,
        ),
        RetrievedChunk(
            chunk_id=second_chunk_id,
            document_id=document_id,
            chunk_index=1,
            content="The recruiter schedules the first conversation.",
            heading_path=["Recruiting"],
            page_start=2,
            page_end=2,
            score=0.8,
        ),
    ]
    document = SimpleNamespace(
        id=document_id,
        status=DocumentStatus.READY,
        original_filename="interview-guide.md",
        document_metadata={"embedding_space": embedding_space_for_provider(embedding_provider)},
    )
    service = QuestionAnsweringService(
        FakeSession(),
        Settings(embedding_dimensions=3),
        embedding_provider=embedding_provider,
        answer_provider=StubAnswerProvider(generated),
        retriever=FakeRetriever(chunks),
    )
    service.documents = FakeDocuments(document)
    service.events = FakeEvents()
    return service, document_id, first_chunk_id, second_chunk_id


@pytest.mark.asyncio
async def test_answer_returns_only_explicit_valid_citation() -> None:
    service, document_id, first_chunk_id, _ = make_service(
        GeneratedAnswer("Supported answer", False, [])
    )
    service.answer_provider = StubAnswerProvider(
        GeneratedAnswer("Supported answer", False, [str(first_chunk_id)])
    )

    result = await service.answer(document_id, "How does the process work?")

    assert result.insufficient_evidence is False
    assert [source.chunk_id for source in result.sources] == [first_chunk_id]


@pytest.mark.asyncio
async def test_answer_without_citations_is_insufficient_and_has_no_sources() -> None:
    service, document_id, _, _ = make_service(GeneratedAnswer("Uncited answer", False, []))

    result = await service.answer(document_id, "What happens?")

    assert result.insufficient_evidence is True
    assert result.sources == []


@pytest.mark.asyncio
async def test_answer_with_nonexistent_citation_is_insufficient_and_has_no_sources() -> None:
    service, document_id, _, _ = make_service(
        GeneratedAnswer("Unsupported reference", False, [str(uuid4())])
    )

    result = await service.answer(document_id, "What happens?")

    assert result.insufficient_evidence is True
    assert result.sources == []


@pytest.mark.asyncio
async def test_answer_with_mixed_citations_keeps_only_valid_sources() -> None:
    service, document_id, first_chunk_id, _ = make_service(
        GeneratedAnswer("Partially referenced answer", False, [])
    )
    service.answer_provider = StubAnswerProvider(
        GeneratedAnswer("Partially referenced answer", False, [str(first_chunk_id), str(uuid4())])
    )

    result = await service.answer(document_id, "What happens?")

    assert result.insufficient_evidence is False
    assert [source.chunk_id for source in result.sources] == [first_chunk_id]


@pytest.mark.asyncio
async def test_provider_insufficient_evidence_remains_insufficient_without_sources() -> None:
    service, document_id, _, _ = make_service(
        GeneratedAnswer("The document does not say.", True, [])
    )

    result = await service.answer(document_id, "What is not covered?")

    assert result.insufficient_evidence is True
    assert result.sources == []
