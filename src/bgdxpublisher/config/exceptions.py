"""Configuration-domain exceptions."""

from bgdxpublisher.exceptions import RuntimeFoundationError


class ConfigurationError(RuntimeFoundationError):
    """Base class for configuration errors."""


class ConfigurationFileError(ConfigurationError):
    """Raised when a configuration file cannot be read or parsed."""


class ConfigurationValidationError(ConfigurationError):
    """Raised when configuration values fail validation."""


class ConfigurationAlreadyLoadedError(ConfigurationError):
    """Raised when configuration is loaded more than once."""


class ConfigurationNotLoadedError(ConfigurationError):
    """Raised when configuration is accessed before loading."""
