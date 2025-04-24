import logging

logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)

# Консольный хендлер
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Формат логов
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
