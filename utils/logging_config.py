import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para terminal"""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m',  # Magenta
        'ENDC': '\033[0m'       # End color
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['ENDC'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['ENDC']}"
        return super().format(record)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configurar logging para la aplicación"""

    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(ColoredFormatter(format_string, date_format))

    handlers = [console_handler]

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter(format_string, date_format))
        handlers.append(file_handler)

    for handler in handlers:
        root_logger.addHandler(handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
