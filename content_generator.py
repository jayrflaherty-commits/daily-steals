from __future__ import annotations
"""
content_generator.py — Daily Steals content generation via Claude.

Generates a daily curated deals email. The deals are editorially framed
(not a raw price list) to drive high engagement and affiliate clicks.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

import anthropic

_FILE_DIR = Path(__file__).parent
BASE_DIR = _FILE_DIR.parent if (_FILE_DIR.parent / "shared").exists() else _FILE_DIR
sys.path.insert(0, str(BASE_DIR))

from shared.topic_tracker import get_recent_topics, format_topics_for_prompt, log_topic
import config

SYSTEM_PROMPT = """You are the editor of "Daily Steals," a daily email newsletter for savvy deal-hunters aged 35–70. Your voice is energetic, friendly, and deal-obsessed — like a best friend who always finds the best prices.

NEWSLETTER FORMULA:
1. One "Deal of the Day" — the single best find, framed with urgency and value
2. "Today's Stack" — 5–7 curated deals across categories (electronics, home, travel, food, subscriptions, free trials, cashback offers)
3. "Free & Freemium" — 1–2 genuinely free things readers can grab today
4. "Steal Alert" — a limited-time or expiring deal that needs action now
5. A warm, punchy sign-off with next day teaser

TONE: Excited but trustworthy. Never shout-y. Always specific (include the regular price vs. deal price when possible). Deals should feel like insider tips, not ads.

IMPORTANT: Include both physical product deals AND digital/subscription deals. Mix categories so every reader finds something relevant.

Output JSON only. No markdown, no explanation."""

CONTENT_SCHEMA = """
{
  "subject_line": "35-50 char subject, specific savings or offer highlighted",
  "preview_text": "80-100 char preheader, extends the subject line's hook",
  "title": "Web version title",
  "topic_slug": "short-kebab-case-identifier e.g. amazon-spring-sale-2026",
  "hook": "2 sentences. Open with the most exciting deal or theme of the day.",
  "deal_of_the_day": {
    "product": "Product/service name",
    "regular_price": "$XX.XX or 'normally $XX/mo'",
    "deal_price": "$XX.XX or 'free trial' or 'X% off'",
    "where": "Amazon / Target / directly at URL",
    "why_worth_it": "1-2 sentences on why this deal is exceptional"
  },
  "todays_stack": [
    {"item": "name", "deal": "price or discount", "where": "retailer", "blurb": "one sentence"},
    {"item": "...", "deal": "...", "where": "...", "blurb": "..."},
    {"item": "...", "deal": "...", "where": "...", "blurb": "..."},
    {"item": "...", "deal": "...", "where": "...", "blurb": "..."},
    {"item": "...", "deal": "...", "where": "...", "blurb": "..."}
  ],
  "free_picks": [
    {"item": "name", "blurb": "what it is and how to get it"}
  ],
  "steal_alert": "1-2 sentences on a time-sensitive deal expiring soon",
  "sponsor_placeholder": "2-3 sentences of native ad copy for our affiliate partner (cashback app, deal site, or subscription service)",
  "cta_text": "Short button label e.g. 'Shop the deal →'",
  "signoff": "1 warm sentence + teaser for tomorrow"
}"""


def generate_content(for_date: date | None = None) -> dict:
    """
    Generates a full Daily Steals issue for the given date.
    Injects recent topics to avoid repetition.
    """
    if for_date is None:
        for_date = date.today()

    recent_topics = get_recent_topics(config.NEWSLETTER_DIR, days=365)
    no_repeat_block = format_topics_for_prompt(recent_topics)

    date_str = for_date.strftime("%A, %B %d, %Y")

    user_prompt = f"""Generate a Daily Steals newsletter for {date_str}.

{no_repeat_block}

Include a good mix of:
- Amazon deals (we earn via Associates tag retirehub09-20)
- Subscription deals (streaming, software, apps)
- Seasonal/timely deals for {for_date.strftime("%B")}
- At least one travel or experience deal
- At least one free offer

Return valid JSON matching this schema:
{CONTENT_SCHEMA}"""

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    content = json.loads(raw)

    # Log topic to tracker
    log_topic(
        newsletter_name=config.NEWSLETTER_DIR,
        topic_slug=content.get("topic_slug", f"deals-{for_date.isoformat()}"),
        subject_line=content.get("subject_line", ""),
        published_date=for_date,
    )

    return content


def format_content_for_template(content: dict) -> dict:
    """
    Converts raw generated content into the shape expected by email_template.build_email_html().
    Daily Steals has a unique structure so we build the main_story and quick_hits here.
    """
    deal = content.get("deal_of_the_day", {})
    stack = content.get("todays_stack", [])
    free_picks = content.get("free_picks", [])
    steal_alert = content.get("steal_alert", "")

    deal_block = (
        f"🔥 <strong>Deal of the Day:</strong> {deal.get('product', '')} — "
        f"was {deal.get('regular_price', '')}, now <strong>{deal.get('deal_price', '')}</strong> "
        f"at {deal.get('where', '')}. {deal.get('why_worth_it', '')}"
    ) if deal else ""

    stack_items = [
        f"<strong>{s['item']}</strong> — {s['deal']} at {s['where']}. {s['blurb']}"
        for s in stack
    ]

    free_items = [f"FREE: {f['item']} — {f['blurb']}" for f in free_picks]

    quick_hits = stack_items + free_items
    if steal_alert:
        quick_hits.append(f"⏰ <strong>Steal Alert:</strong> {steal_alert}")

    return {
        "hook": content.get("hook", ""),
        "main_story": deal_block,
        "quick_hits": quick_hits[:7],
        "sponsor_placeholder": content.get("sponsor_placeholder", ""),
        "money_move": f"Today's top pick: {deal.get('product', '')} for just {deal.get('deal_price', '')}.",
        "cta_text": content.get("cta_text", "Shop the deal →"),
        "cta_url": "#",  # Replace with real affiliate link
        "signoff": content.get("signoff", ""),
        "title": content.get("title", "Daily Steals"),
    }
