import logging

# Configure the logger using basicConfig
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("error.log", mode="w", encoding="utf-8"),
    ],
)

# Set the level for the file handler to ERROR
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.ERROR)

# Create a logger instance
logger = logging.getLogger("my_logger")

# Set the level for the logger to INFO
logger.setLevel(logging.INFO)
