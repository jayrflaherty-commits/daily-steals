"""
main.py — Daily Steals newsletter entry point.

Usage:
    python main.py              # Generate and schedule today's issue
    python main.py --draft      # Post as draft (no scheduled send)
    python main.py --preview    # Print to console, don't post
    python main.py --date 2026-03-10
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

_FILE_DIR = Path(__file__).parent
BASE_DIR = _FILE_DIR.parent if (_FILE_DIR.parent / "shared").exists() else _FILE_DIR
sys.path.insert(0, str(BASE_DIR))

import config
from content_generator import generate_content, format_content_for_template
from affiliates import get_daily_affiliate
from shared.beehiiv_client import BeehiivClient
from shared.email_template import build_email_html, get_theme


def main():
    parser = argparse.ArgumentParser(description="Daily Steals newsletter generator")
    parser.add_argument("--draft",   action="store_true", help="Post as draft")
    parser.add_argument("--preview", action="store_true", help="Preview only, don't post")
    parser.add_argument("--date",    type=str, default=None, help="Date override YYYY-MM-DD")
    args = parser.parse_args()

    if not args.preview:
        config.validate()

    for_date = date.fromisoformat(args.date) if args.date else date.today()
    print(f"\n{'='*55}")
    print(f"  Daily Steals — {for_date.strftime('%A, %B %d, %Y')}")
    print(f"{'='*55}\n")

    print("Generating content via Claude...")
    raw_content = generate_content(for_date=for_date)

    # Inject affiliate link into CTA
    affiliate = get_daily_affiliate(for_date)
    raw_content["cta_url"] = affiliate["url"]
    raw_content["cta_text"] = affiliate.get("cta", "See the deal →")

    template_content = format_content_for_template(raw_content)
    theme = get_theme(config.NEWSLETTER_DIR)
    html = build_email_html(content=template_content, theme=theme)

    subject      = raw_content.get("subject_line", f"Today's steals — {for_date.strftime('%b %d')}")
    preview_text = raw_content.get("preview_text", "Your daily dose of deals.")

    print(f"Subject:  {subject}")
    print(f"Preview:  {preview_text}")
    print(f"Affiliate: {affiliate['name']}")

    if args.preview:
        print("\n--- HTML PREVIEW (first 500 chars) ---")
        print(html[:500])
        print("\n[PREVIEW MODE — nothing posted]")
        return

    client = BeehiivClient(api_key=config.BEEHIIV_API_KEY, publication_id=config.BEEHIIV_PUBLICATION_ID)
    post = client.create_post(
        subject=subject,
        content_html=html,
        preview_text=preview_text,
        draft=args.draft,
        tags=["daily-steals", for_date.isoformat()],
        send_hour_et=config.SEND_HOUR,
        send_minute_et=config.SEND_MINUTE,
    )

    status = "DRAFT" if args.draft else "SCHEDULED"
    print(f"\n✅ {status}: {post.get('id', 'unknown')}")
    print(f"   URL: {post.get('web_url', 'N/A')}")


if __name__ == "__main__":
    main()
