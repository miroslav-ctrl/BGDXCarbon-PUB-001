"""Tests for deterministic pipeline execution and failure handling."""

import logging
from dataclasses import dataclass
from typing import ClassVar

import pytest

from bgdxpublisher.pipeline import (
    PipelineContext,
    PipelineDefinitionError,
    PipelineEngine,
    PipelineExecutionError,
    PipelineFailure,
    PipelineInputContractError,
    PipelineOutputContractError,
    PipelineResult,
    PipelineStage,
    PipelineStatus,
)


@dataclass
class AddStage:
    """Test stage that adds a fixed amount to its integer input."""

    name: str
    amount: int
    order: ClassVar[list[str]] = []
    input_type: type[object] = int
    output_type: type[object] = int

    def execute(self, value: object, context: PipelineContext) -> object:
        """Record invocation order and return a numeric output."""
        self.order.append(self.name)
        return value + self.amount  # type: ignore[operator]


@dataclass
class BrokenStage:
    """Test stage that raises an error containing confidential input."""

    name: str = "broken"
    input_type: type[object] = str
    output_type: type[object] = str

    def execute(self, value: object, context: PipelineContext) -> object:
        """Fail with the current input to verify error/log handling."""
        raise RuntimeError(str(value))


@dataclass
class WrongOutputStage:
    """Test stage that violates its declared output contract."""

    name: str = "wrong-output"
    input_type: type[object] = int
    output_type: type[object] = str

    def execute(self, value: object, context: PipelineContext) -> object:
        """Return the wrong type."""
        return value


def test_pipeline_preserves_order_and_is_deterministic() -> None:
    AddStage.order.clear()
    engine = PipelineEngine((AddStage("first", 2), AddStage("second", 3)))

    first = engine.execute(1)
    second = engine.execute(1)

    assert first == second
    assert first.status is PipelineStatus.COMPLETED
    assert first.output == 6
    assert first.completed_stages == ("first", "second")
    assert AddStage.order == ["first", "second", "first", "second"]


def test_empty_pipeline_returns_unchanged_success() -> None:
    result = PipelineEngine().execute({"unchanged": True})

    assert result.status is PipelineStatus.COMPLETED
    assert result.output == {"unchanged": True}
    assert result.completed_stages == ()
    assert result.failure is None


def test_pipeline_cleans_up_in_reverse_order_after_failure() -> None:
    cleaned: list[str] = []
    context = PipelineContext()
    context.register_cleanup(lambda: cleaned.append("first"))
    context.register_cleanup(lambda: cleaned.append("second"))

    with pytest.raises(PipelineExecutionError) as error:
        PipelineEngine((BrokenStage(),)).execute("confidential-value", context)

    assert cleaned == ["second", "first"]
    assert error.value.__cause__ is not None
    assert error.value.result.status is PipelineStatus.FAILED
    assert error.value.result.output is None
    assert error.value.result.completed_stages == ()
    assert error.value.failure.error_code == "PIPELINE_STAGE_FAILED"
    assert error.value.failure.exception_type == "RuntimeError"


def test_input_contract_failure_is_structured_and_cleans_up() -> None:
    cleaned: list[bool] = []
    context = PipelineContext()
    context.register_cleanup(lambda: cleaned.append(True))

    with pytest.raises(PipelineExecutionError) as error:
        PipelineEngine((AddStage("integer-only", 1),)).execute("no", context)

    assert cleaned == [True]
    assert isinstance(error.value.__cause__, PipelineInputContractError)
    assert error.value.failure.error_code == "PIPELINE_INPUT_INVALID"


def test_output_contract_failure_is_structured() -> None:
    with pytest.raises(PipelineExecutionError) as error:
        PipelineEngine((WrongOutputStage(),)).execute(1)

    assert isinstance(error.value.__cause__, PipelineOutputContractError)
    assert error.value.failure.error_code == "PIPELINE_OUTPUT_INVALID"
    assert error.value.result.output is None


def test_cleanup_errors_are_reported_after_all_cleanup_attempts() -> None:
    cleaned: list[str] = []
    context = PipelineContext()

    def fail_cleanup() -> None:
        cleaned.append("failed")
        raise OSError("hidden detail")

    context.register_cleanup(lambda: cleaned.append("last"))
    context.register_cleanup(fail_cleanup)

    with pytest.raises(PipelineExecutionError) as error:
        PipelineEngine().execute(None, context)

    assert cleaned == ["failed", "last"]
    assert error.value.failure.stage_name == "cleanup"
    assert error.value.failure.error_code == "PIPELINE_CLEANUP_FAILED"
    assert error.value.failure.cleanup_exception_types == ("OSError",)


def test_stage_failure_and_cleanup_failure_are_both_reported() -> None:
    context = PipelineContext()

    def fail_cleanup() -> None:
        raise OSError("hidden detail")

    context.register_cleanup(fail_cleanup)
    with pytest.raises(PipelineExecutionError) as error:
        PipelineEngine((BrokenStage(),)).execute("sensitive", context)

    assert error.value.failure.stage_name == "broken"
    assert error.value.failure.cleanup_exception_types == ("OSError",)


def test_pipeline_definition_rejects_duplicate_names_and_missing_contracts() -> None:
    with pytest.raises(PipelineDefinitionError):
        PipelineEngine((AddStage("duplicate", 1), AddStage("duplicate", 2)))
    with pytest.raises(PipelineDefinitionError):
        PipelineEngine((AddStage(" ", 1),))
    with pytest.raises(PipelineDefinitionError):
        PipelineEngine((AddStage("integer", 1), BrokenStage()))  # type: ignore[arg-type]

    @dataclass
    class MissingTypeStage:
        name: str = "missing-type"
        input_type: object = int
        output_type: object = "not-a-type"

        def execute(self, value: object, context: PipelineContext) -> object:
            """Return the input unchanged."""
            return value

    with pytest.raises(PipelineDefinitionError):
        PipelineEngine((MissingTypeStage(),))  # type: ignore[arg-type]


def test_pipeline_stage_failure_does_not_log_exception_content(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("bgdxpublisher.test.pipeline")
    caplog.set_level(logging.INFO, logger=logger.name)

    with pytest.raises(PipelineExecutionError):
        PipelineEngine((BrokenStage(),), logger).execute("confidential-document-text")

    assert "Pipeline stage started" in caplog.text
    assert "confidential-document-text" not in caplog.text
    assert "RuntimeError" not in caplog.text


def test_pipeline_context_attributes_are_read_only() -> None:
    context = PipelineContext(attributes={"key": "value"})

    with pytest.raises(TypeError):
        context.attributes["key"] = "changed"  # type: ignore[index]


def test_pipeline_context_runs_cleanup_once() -> None:
    called: list[bool] = []
    context = PipelineContext()
    context.register_cleanup(lambda: called.append(True))

    assert context.close() == ()
    assert context.close() == ()
    assert called == [True]
    with pytest.raises(RuntimeError, match="already closed"):
        context.register_cleanup(lambda: None)


def test_pipeline_result_rejects_inconsistent_status_and_output() -> None:
    failure = PipelineFailure("broken", "PIPELINE_STAGE_FAILED", "RuntimeError")
    with pytest.raises(ValueError, match="status and failure"):
        PipelineResult(
            PipelineStatus.COMPLETED,
            None,
            (),
            failure=failure,
        )
    with pytest.raises(ValueError, match="partial output"):
        PipelineResult(
            PipelineStatus.FAILED,
            "partial",
            (),
            failure=failure,
        )


def test_pipeline_execution_error_requires_failed_result() -> None:
    with pytest.raises(ValueError, match="requires a failed result"):
        PipelineExecutionError(PipelineResult(PipelineStatus.COMPLETED, None, ()))


def test_pipeline_stage_protocol_has_documented_contract() -> None:
    stage: PipelineStage = AddStage("protocol", 1)

    assert stage.input_type is int


@pytest.mark.parametrize("execute", [None, 42, "not-callable"])
def test_pipeline_definition_rejects_non_callable_execute(execute: object) -> None:
    class NonCallableStage:
        name = "non-callable"
        input_type = int
        output_type = int

    stage = NonCallableStage()
    stage.execute = execute  # type: ignore[attr-defined]
    with pytest.raises(PipelineDefinitionError, match="callable execute"):
        PipelineEngine((stage,))  # type: ignore[arg-type]


def test_pipeline_definition_rejects_missing_execute() -> None:
    class MissingExecuteStage:
        name = "missing-execute"
        input_type = int
        output_type = int

    with pytest.raises(PipelineDefinitionError, match="callable execute"):
        PipelineEngine((MissingExecuteStage(),))  # type: ignore[arg-type]
