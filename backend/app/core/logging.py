"""JSON logs to stdout. CloudWatch (awslogs driver / agent) picks these up directly."""
import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
