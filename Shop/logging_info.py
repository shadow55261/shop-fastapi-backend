from loguru import logger
logger.add(
    "file_info.log",
    enqueue=True,
    level="INFO",
    filter=lambda record: record["level"].name == "INFO", 
    format="{message} - {level} - {time}"
        )
logger.add(
    "file_error.log", 
    enqueue=True,
    level="WARNING",
    format="{message} - {level} - {time}" 
    )

def log_message(message, level):
    level = level.upper()
    if level == "WARNING":
        logger.warning(str(message))
    elif level == "INFO":
        logger.info(str(message))