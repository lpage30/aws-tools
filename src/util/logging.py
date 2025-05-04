import logging
import sys


def initialize_logging(log_level: str) -> None:
    logging.basicConfig(
        stream=sys.stderr,
        format="[%(asctime)s][%(levelname)s]: %(message)s",
    )

    # Set the log level only for our logger by default
    get_default_logger().setLevel(log_level.upper())


def get_default_logger() -> logging.Logger:
    return logging.getLogger("aws-tools")