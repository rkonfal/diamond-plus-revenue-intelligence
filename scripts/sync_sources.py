#!/usr/bin/env python3
from __future__ import annotations

import json
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
    'klaviyo_overview.json',
    'portal_summary.json',
    'eshop_ytd.json',
    'wpj_orders_previous_day.json',
    'top_50_customers_last_year.json',
]

OPTIONAL_FILES = [
    'customer_fact_ytd_window.json',
    'order_fact_ytd_window.json',
    'ga4_purchase_journey_window.json',
    'customer_attribution_truth.json',
    'campaign_customer_truth.json',
    'customer_attribution_readiness.json',
]

DEFAULT_BASE = 'https://raw.githubusercontent.com/rkonfal/diamond-plus-reporting-preview/main/data/current'
ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / 'source' / 'current'


def compact_customer_fact(payload: dict) -> dict:
    customers = payload.get('customers') or []
    ranked = sorted(customers, key=lambda row: float(row.get('revenueWithVat') or 0), reverse=True)
    return {
        'generatedAt': payload.get('generatedAt'),
        'window': payload.get('window'),
        'summary': payload.get('summary'),
        'customersCount': payload.get('customersCount'),
        'ordersProcessed': payload.get('ordersProcessed'),
        'customers': ranked[:120],
    }


def compact_order_fact(payload: dict) -> dict:
    orders = payload.get('orders') or []
    return {
        'generatedAt': payload.get('generatedAt'),
        'window': payload.get('window'),
        'summary': payload.get('summary'),
        'orders': orders[:250],
    }


def maybe_write_compact(name: str, dest: Path):
    if name == 'customer_fact_ytd_window.json':
        payload = json.loads(dest.read_text())
        compact = compact_customer_fact(payload)
        compact_path = dest.with_name('customer_fact_ytd_compact.json')
        compact_path.write_text(json.dumps(compact, ensure_ascii=False, indent=2), encoding='utf-8')
        dest.unlink(missing_ok=True)
        print(f'Compacted {name} -> {compact_path.name}')
    elif name == 'order_fact_ytd_window.json':
        payload = json.loads(dest.read_text())
        compact = compact_order_fact(payload)
        compact_path = dest.with_name('order_fact_ytd_compact.json')
        compact_path.write_text(json.dumps(compact, ensure_ascii=False, indent=2), encoding='utf-8')
        dest.unlink(missing_ok=True)
        print(f'Compacted {name} -> {compact_path.name}')


def main():
    base = os.environ.get('REVENUE_SOURCE_BASE_URL', DEFAULT_BASE).rstrip('/')
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        url = f'{base}/{name}'
        dest = TARGET / name
        with urllib.request.urlopen(url) as response:
            dest.write_bytes(response.read())
        print(f'Downloaded {name}')

    for name in OPTIONAL_FILES:
        url = f'{base}/{name}'
        dest = TARGET / name
        try:
            with urllib.request.urlopen(url) as response:
                dest.write_bytes(response.read())
            print(f'Downloaded optional {name}')
            maybe_write_compact(name, dest)
        except Exception:
            print(f'Skipped optional {name}')


if __name__ == '__main__':
    main()
