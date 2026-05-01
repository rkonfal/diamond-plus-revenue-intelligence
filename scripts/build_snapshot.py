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


def pick_focus_month(ga4: dict) -> tuple[dict, str]:
    current = ga4['currentMonth']
    previous = ga4['previousMonth']
    if round2(current.get('purchaseRevenue')) == 0:
        return previous, 'previous_month'
    return current, 'current_month'


def top_campaigns(meta: dict, google: dict, sklik: dict) -> list[dict]:
    rows = []
    for row in meta.get('campaignsPreviousMonth', []):
        rows.append({
            'platform': 'Meta Ads',
            'name': row.get('campaignName') or 'Unnamed',
            'spend': round2(row.get('spendCzk')),
            'revenue': round2(row.get('purchaseValueCzk')),
            'roas': row.get('roas'),
            'status': row.get('effectiveStatus') or row.get('status'),
            'risk': 'high' if (row.get('roas') or 0) < 10 else 'medium',
        })
    for row in google.get('campaignsPreviousMonth', []):
        rows.append({
            'platform': 'Google Ads',
            'name': row.get('campaignName') or 'Unnamed',
            'spend': round2(row.get('spendCzk')),
            'revenue': round2(row.get('conversionValueCzk')),
            'roas': row.get('roas'),
            'status': row.get('status'),
            'risk': 'high' if (row.get('roas') or 0) < 15 and round2(row.get('spendCzk')) > 1000 else 'medium',
        })
    for row in sklik.get('campaignPerformancePreviousMonth', []):
        spend = round2(row.get('priceCzk'))
        revenue = round2(row.get('conversionValueCzk'))
        rows.append({
            'platform': 'Sklik',
            'name': row.get('name') or 'Unnamed',
            'spend': spend,
            'revenue': revenue,
            'roas': round(revenue / spend, 2) if spend else None,
            'status': row.get('status'),
            'risk': 'low',
        })
    rows.sort(key=lambda item: item['spend'], reverse=True)
    return rows[:18]


def main():
    meta = read('meta_ads_overview.json')
    google = read('google_ads_overview.json')
    ga4 = read('ga4_overview.json')
    sklik = read('sklik_overview.json')
    finance = read('finance_overview.json')
    marketing = read('marketing_overview.json')
    portal = read('portal_summary.json')
    ytd = read('eshop_ytd.json')
    prev_day = read('wpj_orders_previous_day.json')
    top_customers = read('top_50_customers_last_year.json')

    ga4_focus, focus_key = pick_focus_month(ga4)
    ga4_previous = ga4['previousMonth']
    focus_channels = ga4.get('channelPerformanceCurrentMonth') or []
    if not focus_channels:
        focus_channels = ga4.get('channelPerformance7d') or []

    focus_spend = round2(meta['previousMonth']['spendCzk'] + google['previousMonth']['spendCzk'] + sklik['previousMonth']['total']['priceCzk'])
    finance_prev = finance['previousMonth']
    finance_current = finance['currentMonth']
    previous_day_summary = prev_day['summary']

    snapshot = {
        'generatedAt': ga4.get('generatedAt'),
        'focus': {
            'mode': focus_key,
            'label': ga4_focus['label'],
            'dateFrom': ga4_focus['dateFrom'],
            'dateTo': ga4_focus['dateTo'],
        },
        'executive': {
            'observedRevenue': {
                'value': round2(ga4_focus['purchaseRevenue']),
                'previous': round2(ga4_previous['purchaseRevenue']) if focus_key != 'previous_month' else None,
                'changePct': pct_change(ga4_focus['purchaseRevenue'], ga4_previous['purchaseRevenue']) if focus_key != 'previous_month' else None,
                'label': 'Observed revenue in GA4',
            },
            'mediaSpend': {
                'value': focus_spend,
                'label': 'Paid media spend across Meta, Google and Sklik',
            },
            'blendedRoas': {
                'value': round(ga4_previous['purchaseRevenue'] / focus_spend, 2) if focus_spend else None,
                'label': 'Observed revenue / paid media spend',
            },
            'grossMarginAfterMarketing': {
                'value': round2(finance_prev['afterMarketing']),
                'label': 'Finance after marketing, previous full month',
            },
            'netCashPosition': {
                'value': round2(finance['cash']['netCashPosition']),
                'label': 'Current net cash position',
            },
            'measurementConfidence': {
                'label': 'Medium to low',
                'reason': 'Meta vs GA4 gap, high unattributed traffic, mixed acquisition logic, and incomplete customer classification.',
            },
            'newVsReturning': {
                'status': 'foundation_ready',
                'label': 'Backend customer classification still needs a full historical customer fact table.',
            },
        },
        'businessTruth': {
            'financePreviousMonth': finance_prev,
            'financeCurrentMonth': finance_current,
            'eshopYtdTotals': ytd['totals'],
            'previousDayOrders': {
                'orders': previous_day_summary['orders'],
                'revenueWithVat': round2(previous_day_summary['revenueWithVat']),
                'averageOrderValue': round2(previous_day_summary['averageOrderValue']),
                'cancelledOrders': previous_day_summary['cancelledOrders'],
                'problematicOrders': previous_day_summary['problematicOrders'],
                'czOrders': previous_day_summary['byView']['cz']['orders'],
                'skOrders': previous_day_summary['byView']['sk']['orders'],
            },
            'topCustomersSample': top_customers['top50'][:10],
        },
        'marketingTruth': {
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
                        'PMax incrementality needs separation from remarketing and demand harvesting',
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
            'ga4Channels': focus_channels,
            'marketingOverviewPreviousMonth': marketing['previousMonth'],
            'directSources': marketing['directSources'],
            'topCampaigns': top_campaigns(meta, google, sklik),
        },
        'measurement': {
            'ga4Channels': focus_channels,
            'landingPages': ga4['landingPages7d'],
            'topPages': ga4['topPages7d'],
            'countries': ga4['countries7d'],
            'warnings': [
                'High Unassigned share requires taxonomy and channel grouping cleanup.',
                'Paid Social in GA4 is materially weaker than Meta platform-reported revenue.',
                'Current model still needs backend customer fact logic for true new vs returning measurement.',
            ],
        },
        'auditWorkspace': {
            'topCampaigns': top_campaigns(meta, google, sklik),
            'actions': [
                'Separate acquisition, remarketing, retention, and brand into explicit reporting layers.',
                'Build customer fact table with first confirmed purchase date to unlock true new-vs-returning classification.',
                'Introduce channel confidence scoring based on platform vs GA4 vs backend deltas.',
                'Tighten audience exclusions and tracking governance before trusting platform-reported growth.',
                'Use finance after-marketing and cash views as first-class management outputs, not side panels.',
            ],
        },
        'productStage': {
            'name': 'Stage 1, live prototype with backend truth foundation',
            'done': [
                'Separate repo and product architecture',
                'Static-first live app scaffold',
                'Live marketing and analytics snapshot',
                'Backend truth blocks from finance and order pulse',
                'Campaign audit workspace foundation',
            ],
            'next': [
                'Full customer fact model for new vs returning',
                'Refund / cancellation adjusted contribution logic',
                'Creative-level drilldown and operator workflows',
                'Anomaly detection and alert system',
            ],
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {OUTPUT}')


if __name__ == '__main__':
    main()
