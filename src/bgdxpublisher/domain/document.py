"""Immutable document models and request validation."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import TypeAlias, cast
from uuid import UUID, uuid4

from .exceptions import DocumentValidationError
from .validation import ValidationIssue, ValidationResult

JsonValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | tuple["JsonValue", ...]
    | Mapping[str, "JsonValue"]
)


class DocumentType(str, Enum):
    """Document formats supported by the publisher domain."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"


@dataclass(frozen=True, slots=True)
class DocumentRequest:
    """Untrusted input used to validate and create a document."""

    document_type: object
    title: object
    source_reference: object
    metadata: object = field(default_factory=dict)
    document_id: object = None
    created_at: object = None


def validate_document_request(request: DocumentRequest) -> ValidationResult:
    """Validate required document fields and recursively check metadata."""
    issues: list[ValidationIssue] = []
    if not isinstance(request.document_type, (str, DocumentType)):
        issues.append(
            ValidationIssue(
                "DOCUMENT_TYPE_UNSUPPORTED",
                "document_type",
                "Unsupported document type.",
            )
        )
    else:
        try:
            DocumentType(request.document_type)
        except ValueError:
            issues.append(
                ValidationIssue(
                    "DOCUMENT_TYPE_UNSUPPORTED",
                    "document_type",
                    "Unsupported document type.",
                )
            )

    if not isinstance(request.title, str) or not request.title.strip():
        issues.append(ValidationIssue("TITLE_REQUIRED", "title", "Title is required."))
    if (
        not isinstance(request.source_reference, str)
        or not request.source_reference.strip()
    ):
        issues.append(
            ValidationIssue(
                "SOURCE_REFERENCE_REQUIRED",
                "source_reference",
                "Source reference is required.",
            )
        )
    if request.document_id is not None:
        try:
            UUID(str(request.document_id))
        except (ValueError, TypeError, AttributeError):
            issues.append(
                ValidationIssue(
                    "DOCUMENT_ID_INVALID",
                    "document_id",
                    "Document identifier must be a UUID.",
                )
            )
    if request.created_at is not None and (
        not isinstance(request.created_at, datetime)
        or request.created_at.utcoffset() is None
    ):
        issues.append(
            ValidationIssue(
                "CREATED_AT_INVALID",
                "created_at",
                "Creation timestamp must be timezone-aware.",
            )
        )
    issues.extend(_metadata_issues(request.metadata))
    return ValidationResult(tuple(issues))


@dataclass(frozen=True, slots=True)
class Document:
    """Validated immutable document descriptor."""

    document_type: DocumentType
    title: str
    source_reference: str
    metadata: Mapping[str, JsonValue] = field(default_factory=dict)
    document_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate fields and recursively freeze metadata values."""
        request = DocumentRequest(
            document_type=self.document_type,
            title=self.title,
            source_reference=self.source_reference,
            metadata=self.metadata,
            document_id=self.document_id,
            created_at=self.created_at,
        )
        result = validate_document_request(request)
        if not result.is_valid:
            raise DocumentValidationError(result)
        object.__setattr__(self, "document_type", DocumentType(self.document_type))
        object.__setattr__(self, "document_id", str(UUID(str(self.document_id))))
        object.__setattr__(self, "created_at", self.created_at.astimezone(timezone.utc))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_request(cls, request: DocumentRequest) -> Document:
        """Create a document from validated untrusted input."""
        result = validate_document_request(request)
        if not result.is_valid:
            raise DocumentValidationError(result)
        return cls(
            document_type=DocumentType(request.document_type),
            title=cast(str, request.title),
            source_reference=cast(str, request.source_reference),
            metadata=cast(Mapping[str, JsonValue], request.metadata),
            document_id=str(request.document_id or uuid4()),
            created_at=cast(datetime, request.created_at or datetime.now(timezone.utc)),
        )


def _metadata_issues(value: object) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(value, Mapping):
        return [
            ValidationIssue(
                "METADATA_INVALID", "metadata", "Metadata must be a mapping."
            )
        ]

    def check(item: object, path: str, active: set[int], depth: int) -> None:
        if depth > 32:
            issues.append(
                ValidationIssue(
                    "METADATA_TOO_DEEP",
                    path,
                    "Metadata nesting exceeds the supported depth.",
                )
            )
            return
        if item is None or isinstance(item, (str, bool, int)):
            return
        if isinstance(item, float):
            if not math.isfinite(item):
                issues.append(
                    ValidationIssue(
                        "METADATA_NUMBER_INVALID",
                        path,
                        "Metadata numbers must be finite.",
                    )
                )
            return
        if isinstance(item, Mapping):
            identity = id(item)
            if identity in active:
                issues.append(
                    ValidationIssue(
                        "METADATA_CYCLE", path, "Metadata cannot contain cycles."
                    )
                )
                return
            active.add(identity)
            for key, child in item.items():
                child_path = f"{path}.{key}" if isinstance(key, str) else path
                if not isinstance(key, str):
                    issues.append(
                        ValidationIssue(
                            "METADATA_KEY_INVALID",
                            path,
                            "Metadata keys must be strings.",
                        )
                    )
                else:
                    check(child, child_path, active, depth + 1)
            active.remove(identity)
            return
        if isinstance(item, (list, tuple)):
            identity = id(item)
            if identity in active:
                issues.append(
                    ValidationIssue(
                        "METADATA_CYCLE", path, "Metadata cannot contain cycles."
                    )
                )
                return
            active.add(identity)
            for index, child in enumerate(item):
                check(child, f"{path}[{index}]", active, depth + 1)
            active.remove(identity)
            return
        issues.append(
            ValidationIssue(
                "METADATA_VALUE_INVALID",
                path,
                "Metadata values must be JSON-compatible.",
            )
        )

    check(value, "metadata", set(), 0)
    return issues


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, JsonValue]:
    """Copy metadata into nested read-only mappings and tuples."""
    return MappingProxyType({key: _freeze_value(child) for key, child in value.items()})


def _freeze_value(value: object) -> JsonValue:
    """Recursively convert validated JSON-compatible values to immutable ones."""
    if isinstance(value, Mapping):
        return _freeze_mapping(value)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(child) for child in value)
    return cast(JsonValue, value)
