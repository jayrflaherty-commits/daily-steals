"""affiliates.py — Affiliate links for Daily Steals newsletter."""

from datetime import date
from typing import Optional

AMAZON_ASSOCIATE_TAG = "retirehub09-20"

AFFILIATE_LINKS = {
    "cashback": {
        "name": "Rakuten cashback portal",
        "description": "Earn cash back at 3,500+ stores — free to join, pays quarterly",
        "cta": "Activate my cashback →",
        "url": "https://YOUR_RAKUTEN_AFFILIATE_LINK_HERE",
        # Rakuten: https://www.rakuten.com/affiliates — CJ Affiliate or direct
        # Commission: $10–25 per new member signup | 30-day cookie
    },
    "deals_app": {
        "name": "Capital One Shopping",
        "description": "Free browser extension that auto-finds better prices and coupons while you shop",
        "cta": "Add it free →",
        "url": "https://YOUR_CAPITAL_ONE_SHOPPING_LINK_HERE",
        # Capital One Shopping affiliate: direct program
        # Commission: $5–15 per install + activation
    },
    "subscription_box": {
        "name": "Daily deal subscription picks",
        "description": "The best subscription boxes on sale this week — up to 50% off first box",
        "cta": "See this week's deals →",
        "url": f"https://www.amazon.com/s?k=subscription+box&tag={AMAZON_ASSOCIATE_TAG}",
        # Amazon Associates fallback
    },
    "travel_deals": {
        "name": "Hotel & flight comparison",
        "description": "Compare 500+ booking sites at once — find the lowest price guaranteed",
        "cta": "Search deals →",
        "url": "https://YOUR_KAYAK_OR_HOTELS_AFFILIATE_LINK_HERE",
        # Kayak / Hotels.com / Booking.com via CJ or Impact
        # Commission: 2–4% of booking value | 30-day cookie
    },
    "coupon_site": {
        "name": "RetailMeNot — today's top coupons",
        "description": "Over 500,000 verified coupons from 70,000+ stores — always free",
        "cta": "Browse coupons →",
        "url": "https://YOUR_RETAILMENOT_AFFILIATE_LINK_HERE",
        # RetailMeNot affiliate program via CJ
        # Commission: CPA on referred sales
    },
}

CATEGORY_ORDER = list(AFFILIATE_LINKS.keys())


def get_daily_affiliate(for_date: Optional[date] = None) -> dict:
    if for_date is None:
        for_date = date.today()
    day_index = for_date.toordinal() % len(CATEGORY_ORDER)
    category_key = CATEGORY_ORDER[day_index]
    affiliate = AFFILIATE_LINKS[category_key].copy()
    affiliate["category"] = category_key
    return affiliate


def get_amazon_link(asin: str) -> str:
    return f"https://www.amazon.com/dp/{asin}?tag={AMAZON_ASSOCIATE_TAG}"
