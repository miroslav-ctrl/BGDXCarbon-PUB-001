from .logging import LoggingService
from .runtime import PublisherApplication
from .version import __version__


def main() -> None:
    """Start and stop the runtime foundation."""
    application = PublisherApplication()
    application.initialize()
    application.start()
    application.context.services.resolve(LoggingService).logger.info(
        "BGDXCarbon Publisher Suite %s started.", __version__
    )
    application.stop()


if __name__ == "__main__":
    main()
