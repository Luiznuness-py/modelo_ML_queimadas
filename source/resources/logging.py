import logging
import os
import pathlib
import re
from datetime import datetime
from sys import stdout
from typing import Optional

from source.core.settings import settings

formatter = logging.Formatter(
    '[%(levelname)s]: [%(filename)s line - %(lineno)d] '
    '| Date_Time: %(asctime)s | Function: [%(funcName)s] | Message: ➪ %(message)s '
)

def init_logging(
    name_file_log: str = settings.APP_NAME,
    dev_env: Optional[str] = None,
    enable_file_log: Optional[bool] = None
) -> logging.Logger:

    if dev_env is None:
        dev_env = "DEV" if settings.ENVIRONMENT != "production" else "PROD"

    if enable_file_log is None:
        enable_file_log = settings.LOG_TO_FILE

    # Logger da aplicação
    logger = logging.getLogger(settings.APP_NAME)

    # Evita logs replicarem no root
    logger.propagate = False

    # LIMPAR handlers existentes ANTES de configurar
    logger.handlers.clear()

    # Definir nível
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logger.setLevel(level_map.get(settings.LOG_LEVEL.upper(), logging.INFO))

    # --- STDOUT ---
    stdout_handler = logging.StreamHandler(stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # --- FILE LOG ---
    if enable_file_log:
        try:
            filename_regex = re.compile(r"^[a-zA-Z0-9 -]{1,100}$")

            timestamp = datetime.now().strftime('%Y-%m-%d %H')
            filename = (
                f"{name_file_log} - {timestamp}.log"
                if filename_regex.match(name_file_log)
                else f"Logs - {timestamp}.log"
            )
            env_filename = f'[{dev_env}] {filename}'

            logs_dir = pathlib.Path(getattr(settings, "BASE_DIR", os.getcwd())) / "logs"
            logs_dir.mkdir(exist_ok=True)

            daily_dir = logs_dir / datetime.now().strftime('%Y-%m-%d')
            daily_dir.mkdir(exist_ok=True)

            file_path = daily_dir / env_filename

            file_handler = logging.FileHandler(
                filename=file_path,
                encoding="utf-8",
                mode="a"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"File logging enabled: {file_path}")

        except Exception as e:
            logger.warning(f"Could not initialize file logging: {e}")
            logger.warning("Continuing with console logging only")

    logger.info(
        f"{settings.APP_NAME} logging initialized - Environment: {dev_env}, Level: {settings.LOG_LEVEL}"
    )

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or settings.APP_NAME)

# inicializa no import
main_logger = init_logging()
