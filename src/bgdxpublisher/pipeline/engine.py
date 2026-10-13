"""Deterministic sequential pipeline execution."""

from collections.abc import Sequence
from logging import Logger

from .exceptions import (
    PipelineDefinitionError,
    PipelineExecutionError,
    PipelineInputContractError,
    PipelineOutputContractError,
)
from .models import (
    PipelineContext,
    PipelineFailure,
    PipelineResult,
    PipelineStage,
    PipelineStatus,
)


class PipelineEngine:
    """Execute validated stages sequentially and report failures explicitly."""

    def __init__(
        self,
        stages: Sequence[PipelineStage] = (),
        logger: Logger | None = None,
    ) -> None:
        """Freeze and validate the configured stage order."""
        self._stages = tuple(stages)
        self._logger = logger
        names: set[str] = set()
        for stage in self._stages:
            if not isinstance(stage.name, str) or not stage.name.strip():
                raise PipelineDefinitionError("Pipeline stage names must be non-empty.")
            if stage.name in names:
                raise PipelineDefinitionError(
                    f"Pipeline stage name '{stage.name}' is duplicated."
                )
            names.add(stage.name)
            if not isinstance(stage.input_type, type) or not isinstance(
                stage.output_type, type
            ):
                raise PipelineDefinitionError(
                    f"Pipeline stage '{stage.name}' needs concrete input/output types."
                )
        for previous, following in zip(self._stages, self._stages[1:]):
            if not issubclass(previous.output_type, following.input_type):
                raise PipelineDefinitionError(
                    f"Pipeline stage '{following.name}' input does not accept "
                    f"'{previous.name}' output."
                )

    def execute(
        self,
        value: object,
        context: PipelineContext | None = None,
    ) -> PipelineResult:
        """Execute each stage in its declared order and always clean up context.

        Args:
            value: Input passed to the first stage.
            context: Per-run context shared by all stages.

        Raises:
            PipelineExecutionError: If a stage contract, execution, or cleanup fails.
        """
        run_context = context or PipelineContext()
        completed: list[str] = []
        current = value
        failed_stage: str | None = None
        error_code = ""
        cause: Exception | None = None
        try:
            for stage in self._stages:
                failed_stage = stage.name
                self._log("Pipeline stage started", run_context, stage.name)
                if not isinstance(current, stage.input_type):
                    raise PipelineInputContractError(
                        f"Stage '{stage.name}' input does not satisfy its contract."
                    )
                try:
                    output = stage.execute(current, run_context)
                except Exception as error:
                    error_code = "PIPELINE_STAGE_FAILED"
                    cause = error
                    raise
                if not isinstance(output, stage.output_type):
                    error_code = "PIPELINE_OUTPUT_INVALID"
                    raise PipelineOutputContractError(
                        f"Stage '{stage.name}' output does not satisfy its contract."
                    )
                current = output
                completed.append(stage.name)
                self._log("Pipeline stage completed", run_context, stage.name)
            failed_stage = None
        except PipelineInputContractError as error:
            error_code = "PIPELINE_INPUT_INVALID"
            cause = error
        except PipelineOutputContractError as error:
            cause = error
        except Exception as error:
            error_code = "PIPELINE_STAGE_FAILED"
            cause = error

        cleanup_errors = run_context.close()
        if failed_stage is not None or cleanup_errors:
            stage_name = failed_stage or "cleanup"
            failure = PipelineFailure(
                stage_name=stage_name,
                error_code=error_code or "PIPELINE_CLEANUP_FAILED",
                exception_type=(
                    type(cause).__name__
                    if cause is not None
                    else type(cleanup_errors[0]).__name__
                ),
                cleanup_exception_types=tuple(
                    type(error).__name__ for error in cleanup_errors
                ),
            )
            self._log("Pipeline failed", run_context, stage_name, failure.error_code)
            result = PipelineResult(
                status=PipelineStatus.FAILED,
                output=None,
                completed_stages=tuple(completed),
                failure=failure,
            )
            execution_error = PipelineExecutionError(result)
            if cause is not None:
                raise execution_error from cause
            raise execution_error from cleanup_errors[0]

        self._log("Pipeline completed", run_context, "-")
        return PipelineResult(
            status=PipelineStatus.COMPLETED,
            output=current,
            completed_stages=tuple(completed),
        )

    def _log(
        self,
        message: str,
        context: PipelineContext,
        stage_name: str,
        error_code: str | None = None,
    ) -> None:
        """Log job and stage identifiers without document data or exceptions."""
        if self._logger is None:
            return
        job_id = context.job.job_id if context.job is not None else "-"
        if error_code is None:
            self._logger.info("%s job_id=%s stage=%s", message, job_id, stage_name)
        else:
            self._logger.error(
                "%s job_id=%s stage=%s error_code=%s",
                message,
                job_id,
                stage_name,
                error_code,
            )
