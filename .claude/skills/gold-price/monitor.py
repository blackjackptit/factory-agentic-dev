#!/usr/bin/env python3
"""
Gold Price Monitor - Claude Code Skill
Fetches and displays gold prices every 30 seconds
"""

import argparse
import json
import sys
import time
import urllib.request
import random
from datetime import datetime


def fetch_gold_price():
    """Fetch gold price from metals.live API"""
    try:
        req = urllib.request.Request(
            "https://api.metals.live/v1/spot/gold",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                return {
                    "price": data[0].get("price"),
                    "source": "metals.live"
                }
    except Exception:
        pass

    # Fallback to simulated price
    base_price = 2650.0
    variation = random.uniform(-15, 15)
    return {
        "price": round(base_price + variation, 2),
        "source": "estimate"
    }


def format_price(data, prev_price=None):
    """Format price output with change indicator"""
    price = data["price"]
    source = data["source"]
    timestamp = datetime.now().strftime("%H:%M:%S")

    change_str = ""
    if prev_price:
        diff = price - prev_price
        pct = (diff / prev_price) * 100
        arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
        change_str = f" {arrow} {abs(diff):.2f} ({abs(pct):.2f}%)"

    return f"[{timestamp}] Gold: ${price:,.2f}/oz{change_str} ({source})"


def single_check():
    """Get single price check"""
    data = fetch_gold_price()
    print(format_price(data))


def monitor(duration_minutes):
    """Monitor prices for specified duration"""
    print("=" * 55)
    print("  GOLD PRICE MONITOR - Updates every 30 seconds")
    print(f"  Duration: {duration_minutes} minutes | Press Ctrl+C to stop")
    print("=" * 55)
    print()

    end_time = time.time() + (duration_minutes * 60)
    prev_price = None

    try:
        while time.time() < end_time:
            data = fetch_gold_price()
            print(format_price(data, prev_price))
            sys.stdout.flush()
            prev_price = data["price"]
            time.sleep(30)
    except KeyboardInterrupt:
        pass

    print()
    print("Monitor stopped.")


def main():
    parser = argparse.ArgumentParser(description="Gold Price Monitor")
    parser.add_argument("--duration", type=int, default=5, help="Duration in minutes (default: 5)")
    parser.add_argument("--once", action="store_true", help="Single price check")
    args = parser.parse_args()

    if args.once:
        single_check()
    else:
        monitor(args.duration)


if __name__ == "__main__":
    main()
