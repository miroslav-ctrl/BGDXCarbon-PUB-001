"""Individual runtime diagnostic checks."""

import sys
from collections.abc import Callable
from pathlib import Path

from bgdxpublisher.config import ConfigurationError, LoggingSettings
from bgdxpublisher.container import ServiceRegistry
from bgdxpublisher.logging import LoggerFactory
from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError

from .models import DiagnosticResult, DiagnosticStatus


def check_python_version(
    version: tuple[int, int, int] | None = None,
) -> DiagnosticResult:
    """Check that Python 3.13 or newer is running."""
    actual = tuple(sys.version_info[:3]) if version is None else version
    if actual >= (3, 13, 0):
        return DiagnosticResult(
            "Python", DiagnosticStatus.PASS, f"Python {'.'.join(map(str, actual))}"
        )
    return DiagnosticResult(
        "Python",
        DiagnosticStatus.FAIL,
        f"Python 3.13 or newer is required (found {'.'.join(map(str, actual))}).",
    )


def check_configuration(
    config_path: Path = Path("configs/default.yaml"),
) -> DiagnosticResult:
    """Check that application configuration loads and validates."""
    try:
        PublisherApplication(config_path=config_path).validate_configuration()
    except ConfigurationError as error:
        return DiagnosticResult("Configuration", DiagnosticStatus.FAIL, str(error))
    return DiagnosticResult(
        "Configuration", DiagnosticStatus.PASS, "Configuration is valid."
    )


def check_logging() -> DiagnosticResult:
    """Check that the logging subsystem initializes and releases resources."""
    logging_service = None
    try:
        logging_service = LoggerFactory.create(
            "bgdxpublisher.diagnostics", LoggingSettings(console=False)
        )
    except (OSError, ValueError) as error:
        return DiagnosticResult("Logging", DiagnosticStatus.FAIL, str(error))
    finally:
        if logging_service is not None:
            logging_service.close()
    return DiagnosticResult("Logging", DiagnosticStatus.PASS, "Logging initialized.")


def check_service_registry() -> DiagnosticResult:
    """Check service registry registration and resolution."""

    class RegistryProbe:
        """Marker type for the registry check."""

    registry = ServiceRegistry()
    probe = RegistryProbe()
    registry.register(RegistryProbe, probe)
    if registry.contains(RegistryProbe) and registry.resolve(RegistryProbe) is probe:
        return DiagnosticResult(
            "Service Registry", DiagnosticStatus.PASS, "Registry is operational."
        )
    return DiagnosticResult(
        "Service Registry",
        DiagnosticStatus.FAIL,
        "Registry could not resolve a service.",
    )


def check_runtime(
    config_path: Path = Path("configs/default.yaml"),
    application_factory: Callable[..., PublisherApplication] = PublisherApplication,
) -> DiagnosticResult:
    """Check that the application runtime initializes and shuts down."""
    try:
        application = application_factory(config_path=config_path)
        application.initialize()
        application.start()
        application.stop()
    except (RuntimeFoundationError, ConfigurationError) as error:
        return DiagnosticResult("Runtime", DiagnosticStatus.FAIL, str(error))
    return DiagnosticResult(
        "Runtime", DiagnosticStatus.PASS, "Runtime initialized successfully."
    )


def check_workspace(path: Path | None = None) -> DiagnosticResult:
    """Check that the current workspace can be accessed."""
    workspace = Path.cwd() if path is None else path
    try:
        if not workspace.is_dir():
            raise OSError("Workspace is not a directory.")
        next(workspace.iterdir(), None)
    except OSError as error:
        return DiagnosticResult("Workspace", DiagnosticStatus.FAIL, str(error))
    return DiagnosticResult(
        "Workspace", DiagnosticStatus.PASS, f"Workspace is accessible: {workspace}"
    )


def default_diagnostic_checks(
    config_path: Path = Path("configs/default.yaml"),
) -> tuple[Callable[[], DiagnosticResult], ...]:
    """Build the standard diagnostic checks for the selected configuration."""
    return (
        check_python_version,
        lambda: check_configuration(config_path),
        check_logging,
        check_service_registry,
        lambda: check_runtime(config_path),
        check_workspace,
    )
