#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('/Users/rudolfkonfal/.openclaw/workspace/diamond-plus-revenue-intelligence')
SOURCE = Path('/Users/rudolfkonfal/.openclaw/workspace/reporting-v2/data/current')
OUTPUT = ROOT / 'data' / 'revenue-intelligence-snapshot.json'


def pct_change(cur, prev):
    if prev in (None, 0):
        return None
    return round((cur - prev) / prev * 100, 2)


def read(name: str):
    return json.loads((SOURCE / name).read_text())


def round2(value):
    return round(float(value or 0), 2)


def main():
    meta = read('meta_ads_overview.json')
    google = read('google_ads_overview.json')
    ga4 = read('ga4_overview.json')
    sklik = read('sklik_overview.json')

    ga4_current = ga4['currentMonth']
    ga4_previous = ga4['previousMonth']
    ga4_focus = ga4_previous if round2(ga4_current['purchaseRevenue']) == 0 else ga4_current
    channel_focus = ga4.get('channelPerformanceCurrentMonth') or ga4.get('channelPerformance7d') or []
    if not channel_focus:
        channel_focus = []

    snapshot = {
        'generatedAt': ga4.get('generatedAt'),
        'periods': {
            'focusLabel': 'Previous full month' if ga4_focus is ga4_previous else 'Current month to date',
            'pulseLabel': 'Today / current month pulse',
            'ga4CurrentMonth': ga4_current,
            'ga4PreviousMonth': ga4_previous,
            'ga4Focus': ga4_focus,
        },
        'executive': {
            'backendStyleRevenueProxy': {
                'value': round2(ga4_focus['purchaseRevenue']),
                'previous': round2(ga4_previous['purchaseRevenue']) if ga4_focus is not ga4_previous else None,
                'changePct': pct_change(ga4_focus['purchaseRevenue'], ga4_previous['purchaseRevenue']) if ga4_focus is not ga4_previous else None,
                'label': 'Observed revenue in GA4',
            },
            'paidMediaSpend': {
                'value': round2(meta['previousMonth']['spendCzk'] + google['previousMonth']['spendCzk'] + sklik['previousMonth']['total']['priceCzk']) if ga4_focus is ga4_previous else round2(meta['summary']['spendCzk'] + google['summary']['spendCzk'] + sklik['currentMonth']['total']['priceCzk']),
                'previous': None,
            },
            'pulseToday': {
                'metaSpendToday': round2(meta['summary']['spendCzk']),
                'googleSpendToday': round2(google['summary']['spendCzk']),
                'metaRoasToday': meta['summary']['roas'],
                'googleRoasToday': google['summary']['roas'],
            },
            'newVsReturningPlaceholder': {
                'label': 'Needs backend customer classification',
                'status': 'missing',
            },
            'measurementConfidence': {
                'label': 'Medium to low',
                'reason': 'Meta vs GA4 gap, high Unassigned, inconsistent tracking hygiene',
            },
        },
        'channels': [
            {
                'channel': 'Meta Ads',
                'spend': round2(meta['previousMonth']['spendCzk']),
                'reportedRevenue': round2(meta['previousMonth']['purchaseValueCzk']),
                'roas': meta['previousMonth']['roas'],
                'trust': 'low',
                'notes': [
                    'Prospecting contamination risk',
                    'Audience exclusions need tightening',
                    'Platform revenue materially diverges from GA4',
                ],
            },
            {
                'channel': 'Google Ads',
                'spend': round2(google['previousMonth']['spendCzk']),
                'reportedRevenue': round2(google['previousMonth']['conversionValueCzk']),
                'roas': google['previousMonth']['roas'],
                'trust': 'medium',
                'notes': [
                    'Performance is strongest, but heavily brand-led',
                    'PMax incrementality needs separation from remarketing / demand harvesting',
                    'Tracking templates are not consistently enforced',
                ],
            },
            {
                'channel': 'Sklik',
                'spend': round2(sklik['previousMonth']['total']['priceCzk']),
                'reportedRevenue': round2(sklik['previousMonth']['total']['conversionValueCzk']),
                'roas': round(sklik['previousMonth']['total']['conversionValueCzk'] / sklik['previousMonth']['total']['priceCzk'], 2) if sklik['previousMonth']['total']['priceCzk'] else None,
                'trust': 'low',
                'notes': [
                    'Needs validation against backend and GA4',
                    'Role in the media mix is still unclear',
                ],
            },
        ],
        'ga4Channels': channel_focus,
        'topLandingPages': ga4['landingPages7d'],
        'actions': [
            'Separate acquisition, remarketing, retention, and brand logic into explicit reporting layers.',
            'Build new-vs-returning customer classification from backend orders.',
            'Create channel confidence scoring based on platform vs GA4 vs backend deltas.',
            'Tighten audience exclusions and tracking governance before trusting platform-reported growth.',
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {OUTPUT}')


if __name__ == '__main__':
    main()
