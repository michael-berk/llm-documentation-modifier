import logging


def init_logger(name: str = None):
    logger = logging.getLogger(__name__ if name is None else name)
    logger.setLevel(logging.DEBUG)  # Set minimum level the logger will handle

    # Create console handlers
    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)

    # Create formatters with local time
    local_time_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    info_handler.setFormatter(local_time_format)
    error_handler.setFormatter(local_time_format)

    # Ensure time is in local timestamp
    logging.Formatter.converter = logging.localdate

    # Add handlers to logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger
