#!/usr/bin/env python3
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

FILES = [
    'meta_ads_overview.json',
    'google_ads_overview.json',
    'ga4_overview.json',
    'sklik_overview.json',
    'finance_overview.json',
    'marketing_overview.json',
    'portal_summary.json',
    'eshop_ytd.json',
    'wpj_orders_previous_day.json',
    'top_50_customers_last_year.json',
]

DEFAULT_BASE = 'https://raw.githubusercontent.com/rkonfal/diamond-plus-reporting-preview/main/data/current'
ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / 'source' / 'current'


def main():
    base = os.environ.get('REVENUE_SOURCE_BASE_URL', DEFAULT_BASE).rstrip('/')
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        url = f'{base}/{name}'
        dest = TARGET / name
        with urllib.request.urlopen(url) as response:
            dest.write_bytes(response.read())
        print(f'Downloaded {name}')


if __name__ == '__main__':
    main()
