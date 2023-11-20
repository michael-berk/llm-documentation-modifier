import logging
from logging import Logger


def init_logger() -> Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)

    local_time_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    info_handler.setFormatter(local_time_format)
    error_handler.setFormatter(local_time_format)

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger
