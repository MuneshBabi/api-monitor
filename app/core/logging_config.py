import logging
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir/"app.log"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    handlers=[logging.FileHandler(log_file),
                              logging.StreamHandler()])

logging.getLogger("httpx").setLevel(logging.WARNING)