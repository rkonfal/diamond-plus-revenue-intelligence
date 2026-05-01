from __future__ import annotations


def round2(value):
    return round(float(value or 0), 2)


def pct_change(current, previous):
    if previous in (None, 0):
        return None
    return round((current - previous) / previous * 100, 2)


def pick_focus_month(ga4: dict) -> tuple[dict, str]:
    current = ga4['currentMonth']
    previous = ga4['previousMonth']
    if round2(current.get('purchaseRevenue')) == 0:
        return previous, 'previous_month'
    return current, 'current_month'


def build_top_campaigns(meta: dict, google: dict, sklik: dict) -> list[dict]:
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


def build_channel_truth(meta: dict, google: dict, sklik: dict) -> list[dict]:
    return [
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
    ]
