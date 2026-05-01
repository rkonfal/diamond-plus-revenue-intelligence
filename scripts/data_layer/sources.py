from __future__ import annotations

import json
from pathlib import Path


class SourceStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def read_json(self, name: str):
        return json.loads((self.base_dir / name).read_text())

    def load_all(self) -> dict:
        return {
            'meta': self.read_json('meta_ads_overview.json'),
            'google': self.read_json('google_ads_overview.json'),
            'ga4': self.read_json('ga4_overview.json'),
            'sklik': self.read_json('sklik_overview.json'),
            'finance': self.read_json('finance_overview.json'),
            'marketing': self.read_json('marketing_overview.json'),
            'klaviyo': self.read_json('klaviyo_overview.json'),
            'portal': self.read_json('portal_summary.json'),
            'eshopYtd': self.read_json('eshop_ytd.json'),
            'previousDayOrders': self.read_json('wpj_orders_previous_day.json'),
            'topCustomers': self.read_json('top_50_customers_last_year.json'),
        }
