"""config.py — Daily Steals newsletter configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

NEWSLETTER_NAME        = "Daily Steals"
NEWSLETTER_DIR         = "daily-steals"
TAGLINE                = "The best deals of the day — straight to your inbox"
SEND_HOUR              = 7   # 7:15 AM ET (GitHub Actions offset handles the :15)
TIMEZONE               = "America/New_York"

ANTHROPIC_API_KEY      = os.getenv("ANTHROPIC_API_KEY", "")
BEEHIIV_API_KEY        = os.getenv("DAILY_STEALS_BEEHIIV_API_KEY", os.getenv("BEEHIIV_API_KEY", ""))
BEEHIIV_PUBLICATION_ID = os.getenv("DAILY_STEALS_BEEHIIV_PUBLICATION_ID", "")
CLAUDE_MODEL           = "claude-sonnet-4-5"


def validate():
    missing = [k for k, v in {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "DAILY_STEALS_BEEHIIV_API_KEY": BEEHIIV_API_KEY,
        "DAILY_STEALS_BEEHIIV_PUBLICATION_ID": BEEHIIV_PUBLICATION_ID,
    }.items() if not v]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")
