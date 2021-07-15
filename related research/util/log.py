import inspect
import logging
import logging.handlers


def init_local_logger(level: int):
    previous_frame = inspect.currentframe().f_back
    logger_name = "main"
    if previous_frame:
        logger_name = inspect.getmodule(previous_frame).__name__
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(message)s"
        "\n\tOF %(levelname)s FROM %(name)s"
        "\n\tIN %(funcName)s (%(filename)s:%(lineno)d)"
        "\n\tAT %(asctime)s",
        "%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    error_file = logging.handlers.TimedRotatingFileHandler(
        "error.log", when="h", backupCount=5
    )
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(formatter)
    logger.addHandler(error_file)

    all_file = logging.handlers.TimedRotatingFileHandler(
        "all.log", when="h", backupCount=5
    )
    all_file.setLevel(logging.DEBUG)
    all_file.setFormatter(formatter)
    logger.addHandler(all_file)

    return logger
