import os
import logging
from datetime import datetime

# Create a logger instance
logger = logging.getLogger("main_logger")

# Define the log message format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Configure the logger using basicConfig
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
    ],
)


# Create a custom handler to capture WARNING and higher log messages in the list
class LevelBasedFileHandler(logging.Handler):
    """
    Custom logging handler to capture log messages of a specified level and higher in separate log files.

    Args:
        directory (str, optional): The directory where log files will be stored. Defaults to "logs/".
        mode (str, optional): The file open mode. Defaults to "a" (append).
        min_level (int, optional): The minimum log level to capture in the log file. Defaults to logging.WARNING.
        encoding (str, optional): The file encoding. Defaults to "utf-8".
    """

    def __init__(
        self, directory="logs/", mode="a", min_level=logging.WARNING, encoding="utf-8"
    ):
        super().__init__()
        self.directory = directory
        self.mode = mode
        self.min_level = min_level
        self.encoding = encoding
        self.setFormatter(logging.Formatter(LOG_FORMAT))
        self.log_file_path = None
        # Create the "logs" directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

    def emit(self, record):
        if record.levelno >= self.min_level:
            # Check if the log file path has been created (file name depends on the first appeared log)
            if self.log_file_path is None:
                # Create a timestamp for the filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                self.log_file_path = os.path.join(
                    self.directory, f"{timestamp}_error.log"
                )

            with open(
                self.log_file_path,
                self.mode,
                encoding=self.encoding,
            ) as file:
                file.write(self.format(record) + "\n")


# Add the custom LevelBasedFileHandler to capture log messages of WARNING level and higher
logger.addHandler(LevelBasedFileHandler())
