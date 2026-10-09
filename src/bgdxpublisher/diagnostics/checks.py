"""Individual runtime and environment diagnostic checks.

Broad Exception handling is intentional only at the diagnostic boundary in
SPR-002: unexpected check failures become structured DiagnosticResult failures.
Best-effort cleanup preserves the original failure if cleanup also raises.
This policy does not extend broad handling into other application code.
"""

import sys
from collections.abc import Callable
from pathlib import Path

from bgdxpublisher.config import PublisherSettings
from bgdxpublisher.logging import LoggingService
from bgdxpublisher.runtime import (
    ApplicationMetadata,
    PublisherApplication,
    RuntimeState,
)

from .models import DiagnosticResult, DiagnosticStatus
from .service import DiagnosticCheck


def _result(
    name: str,
    status: DiagnosticStatus,
    message: str,
    mandatory: bool = True,
) -> DiagnosticResult:
    """Create a standard diagnostic result."""
    return DiagnosticResult(name, status, message, mandatory)


def check_python_version() -> DiagnosticResult:
    """Check that the running interpreter meets the Python 3.13 minimum."""
    if sys.version_info >= (3, 13):
        return _result("python_version", DiagnosticStatus.PASS, "Python 3.13 or newer.")
    version = ".".join(str(part) for part in sys.version_info[:3])
    return _result(
        "python_version",
        DiagnosticStatus.FAIL,
        f"Python 3.13 or newer is required; found {version}.",
    )


def check_configuration(config_path: Path | None) -> DiagnosticResult:
    """Validate configuration through the PublisherApplication contract.

    Args:
        config_path: YAML file, or None for the packaged default.
    """
    application = PublisherApplication(config_path=config_path)
    try:
        application.configuration.load()
    except Exception as error:
        return _result("configuration", DiagnosticStatus.FAIL, str(error))
    return _result("configuration", DiagnosticStatus.PASS, "Configuration is valid.")


def _run_application_check(
    name: str,
    config_path: Path | None,
    verify: Callable[[PublisherApplication], str],
) -> DiagnosticResult:
    """Initialize an application, run a check, and close its runtime."""
    application = PublisherApplication(config_path=config_path)
    try:
        application.initialize()
        message = verify(application)
        application.start()
        application.stop()
    except Exception as error:
        try:
            if application.state is RuntimeState.CONFIGURED:
                application.start()
            if application.state is RuntimeState.RUNNING:
                application.stop()
        except Exception:
            pass
        return _result(name, DiagnosticStatus.FAIL, str(error))
    return _result(name, DiagnosticStatus.PASS, message)


def check_logging_initialization(config_path: Path | None) -> DiagnosticResult:
    """Check that application initialization registers a usable logger.

    Args:
        config_path: YAML file, or None for the packaged default.
    """

    def verify(application: PublisherApplication) -> str:
        logging_service = application.context.services.resolve(LoggingService)
        if logging_service.logger.name != "bgdxpublisher":
            raise RuntimeError("Application logger has an unexpected name.")
        return "Logging service initialized."

    return _run_application_check("logging", config_path, verify)


def check_service_registry(config_path: Path | None) -> DiagnosticResult:
    """Check that runtime services can be resolved from the application registry.

    Args:
        config_path: YAML file, or None for the packaged default.
    """

    def verify(application: PublisherApplication) -> str:
        application.context.services.resolve(PublisherSettings)
        application.context.services.resolve(LoggingService)
        return "Registered configuration and logging services are resolvable."

    return _run_application_check("service_registry", config_path, verify)


def check_runtime_initialization(config_path: Path | None) -> DiagnosticResult:
    """Check runtime metadata and lifecycle initialization.

    Args:
        config_path: YAML file, or None for the packaged default.
    """

    def verify(application: PublisherApplication) -> str:
        if not isinstance(application.context.metadata, ApplicationMetadata):
            raise RuntimeError("Application metadata is unavailable.")
        if application.state is not RuntimeState.CONFIGURED:
            raise RuntimeError(f"Unexpected initialized state: {application.state}.")
        return "Runtime initialized and transitioned through its lifecycle."

    return _run_application_check("runtime", config_path, verify)


def check_workspace_accessibility(workspace: Path) -> DiagnosticResult:
    """Check whether a workspace directory can be inspected.

    Args:
        workspace: Directory to inspect.
    """
    try:
        if not workspace.is_dir():
            raise NotADirectoryError(f"{workspace} is not a directory.")
        next(workspace.iterdir(), None)
    except OSError as error:
        return _result(
            "workspace",
            DiagnosticStatus.WARNING,
            f"Workspace is not accessible: {error}",
            mandatory=False,
        )
    return _result(
        "workspace",
        DiagnosticStatus.PASS,
        f"Workspace is accessible: {workspace}",
        mandatory=False,
    )


def default_diagnostic_checks(
    config_path: Path | None, workspace: Path | None = None
) -> tuple[DiagnosticCheck, ...]:
    """Build the standard ordered diagnostic suite.

    Args:
        config_path: YAML file, or None for the packaged default.
        workspace: Optional workspace directory; defaults to the current directory.
    """
    selected_workspace = Path.cwd() if workspace is None else workspace
    return (
        DiagnosticCheck("python_version", check_python_version),
        DiagnosticCheck("configuration", lambda: check_configuration(config_path)),
        DiagnosticCheck("logging", lambda: check_logging_initialization(config_path)),
        DiagnosticCheck(
            "service_registry", lambda: check_service_registry(config_path)
        ),
        DiagnosticCheck("runtime", lambda: check_runtime_initialization(config_path)),
        DiagnosticCheck(
            "workspace", lambda: check_workspace_accessibility(selected_workspace)
        ),
    )
