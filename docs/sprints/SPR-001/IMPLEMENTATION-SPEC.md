# SPR-001 Implementation Specification

## Architecture boundaries

The runtime is divided into `runtime`, `config`, `logging`, and `container`
packages under `src/bgdxpublisher`. Runtime lifecycle orchestration composes the
other subsystems; the registry resolves services by their declared Python type.
The work does not add functionality outside the SPR-001 scope.

## Runtime contract

`ApplicationLifecycle` permits only explicit transitions among `NEW`,
`INITIALIZING`, `INITIALIZED`, `RUNNING`, `STOPPING`, `STOPPED`, and `FAILED`.
`PublisherApplication.initialize()` loads validated settings and registers
settings and logging services before entering `INITIALIZED`. `start()` and
`stop()` advance the lifecycle deterministically. Domain exceptions are rooted
at `RuntimeFoundationError`.

## Configuration contract

`PublisherSettings` is a frozen Pydantic v2 model. The YAML root contains `app`
and may contain `runtime`, `logging`, and `environments`. The chosen environment
overlay is recursively merged over base configuration; nested environment
variables with the `BGDXPUBLISHER__` prefix are applied last. File, validation,
and repeated-load errors have separate domain exception types.

## Logging contract

`LoggerFactory` configures standard `logging.Logger` instances with a JSON
formatter containing UTC timestamp, level, logger name, and message. It enables
console output by default and optionally creates a UTF-8 file handler.
`LoggingService.close()` flushes and releases owned handlers.

## Dependencies

Runtime dependencies are Pydantic v2 and PyYAML. Python 3.13 or newer is
required. Development quality tools and test dependencies are in the `dev`
optional dependency group in `pyproject.toml`.
