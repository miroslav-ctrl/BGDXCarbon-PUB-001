"""Tests for immutable document models and structured validation."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from bgdxpublisher.domain import (
    Document,
    DocumentRequest,
    DocumentType,
    DocumentValidationError,
    ValidationIssue,
    ValidationResult,
    validate_document_request,
)


def test_document_normalizes_identity_timestamp_and_freezes_metadata() -> None:
    identifier = str(uuid4()).upper()
    created = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
    metadata = {"tags": ["draft"], "nested": {"approved": False}}

    document = Document(
        document_type=DocumentType.MARKDOWN,
        title="Report",
        source_reference="reports/report.md",
        metadata=metadata,
        document_id=identifier,
        created_at=created,
    )

    metadata["tags"].append("changed")
    assert document.document_id == identifier.lower()
    assert document.created_at == created
    assert document.metadata["tags"] == ("draft",)
    assert document.metadata["nested"]["approved"] is False
    with pytest.raises(TypeError):
        document.metadata["new"] = "value"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        document.title = "Changed"  # type: ignore[misc]


def test_document_request_defaults_identifier_and_timestamp() -> None:
    document = Document.from_request(
        DocumentRequest(
            document_type="html",
            title="Output",
            source_reference="output.html",
        )
    )

    assert DocumentType(document.document_type) is DocumentType.HTML
    assert document.document_id
    assert datetime.fromisoformat(document.created_at.isoformat()).tzinfo is not None


@pytest.mark.parametrize(
    ("document_request", "code"),
    [
        (
            DocumentRequest(
                document_type="unknown",
                title="Title",
                source_reference="source",
            ),
            "DOCUMENT_TYPE_UNSUPPORTED",
        ),
        (
            DocumentRequest(
                document_type="markdown",
                title=" ",
                source_reference="source",
            ),
            "TITLE_REQUIRED",
        ),
        (
            DocumentRequest(
                document_type="markdown",
                title="Title",
                source_reference="",
            ),
            "SOURCE_REFERENCE_REQUIRED",
        ),
        (
            DocumentRequest(
                document_type="markdown",
                title="Title",
                source_reference="source",
                document_id="not-a-uuid",
            ),
            "DOCUMENT_ID_INVALID",
        ),
        (
            DocumentRequest(
                document_type="markdown",
                title="Title",
                source_reference="source",
                created_at=datetime(2026, 1, 1),
            ),
            "CREATED_AT_INVALID",
        ),
        (
            DocumentRequest(
                document_type="markdown",
                title="Title",
                source_reference="source",
                metadata=[],
            ),
            "METADATA_INVALID",
        ),
    ],
)
def test_document_request_returns_stable_validation_codes(
    document_request: DocumentRequest, code: str
) -> None:
    result = validate_document_request(document_request)

    assert not result.is_valid
    assert code in {issue.code for issue in result.errors}
    with pytest.raises(DocumentValidationError) as error:
        Document.from_request(document_request)
    assert error.value.result == result


@pytest.mark.parametrize(
    ("metadata", "code"),
    [
        ({"bad": float("nan")}, "METADATA_NUMBER_INVALID"),
        ({1: "value"}, "METADATA_KEY_INVALID"),
        ({"unsupported": {1, 2}}, "METADATA_VALUE_INVALID"),
    ],
)
def test_metadata_rejects_non_json_values(metadata: object, code: str) -> None:
    result = validate_document_request(
        DocumentRequest("markdown", "Title", "source", metadata=metadata)
    )

    assert code in {issue.code for issue in result.errors}


def test_metadata_rejects_cycles_and_excessive_nesting() -> None:
    cyclic: list[object] = []
    cyclic.append(cyclic)
    too_deep: object = "end"
    for _ in range(34):
        too_deep = [too_deep]

    cycle_result = validate_document_request(
        DocumentRequest("markdown", "Title", "source", metadata={"cycle": cyclic})
    )
    depth_result = validate_document_request(
        DocumentRequest("markdown", "Title", "source", metadata={"nested": too_deep})
    )

    assert "METADATA_CYCLE" in {issue.code for issue in cycle_result.errors}
    assert "METADATA_TOO_DEEP" in {issue.code for issue in depth_result.errors}


def test_document_type_must_be_string_or_supported_enum() -> None:
    result = validate_document_request(DocumentRequest(3, "Title", "source"))

    assert result.errors[0].code == "DOCUMENT_TYPE_UNSUPPORTED"


def test_document_model_raises_structured_error_for_invalid_fields() -> None:
    with pytest.raises(DocumentValidationError) as error:
        Document(DocumentType.MARKDOWN, "", "source")

    assert error.value.result.errors[0].code == "TITLE_REQUIRED"


def test_mapping_metadata_cycles_are_rejected() -> None:
    cyclic: dict[str, object] = {}
    cyclic["self"] = cyclic

    result = validate_document_request(
        DocumentRequest("markdown", "Title", "source", metadata=cyclic)
    )

    assert "METADATA_CYCLE" in {issue.code for issue in result.errors}


def test_non_finite_infinity_is_rejected() -> None:
    result = validate_document_request(
        DocumentRequest("markdown", "Title", "source", metadata={"value": float("inf")})
    )

    assert result.errors[0].code == "METADATA_NUMBER_INVALID"


def test_validation_results_combine_without_mutation() -> None:
    first = ValidationResult((ValidationIssue("FIRST", "first", "First error."),))
    second = ValidationResult((ValidationIssue("SECOND", "second", "Second error."),))

    combined = first.extend(second)

    assert [issue.code for issue in combined.errors] == ["FIRST", "SECOND"]
    assert [issue.code for issue in first.errors] == ["FIRST"]
