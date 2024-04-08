import logging
from datetime import datetime, timedelta

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich.traceback import install

custom_theme = Theme({"success": "grey3 on pale_green1 bold", "error": "grey93 on red bold"})

console = Console(highlight=True, emoji=True, theme=custom_theme, emoji_variant="emoji")

today = datetime.now()
yesterday = today - timedelta(days=1)
last_30_days = today - timedelta(days=30)

install(show_locals=False)

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            console=console,
            markup=True,
        )
    ],
    force=True,
)
logger = logging.getLogger(__name__)
