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


def build_customer_fact(top_customers: dict, ytd: dict) -> dict:
    customers = top_customers.get('top50', [])
    total_customers = top_customers.get('customersCount', 0)
    total_orders = top_customers.get('ordersProcessed', 0)
    total_revenue = round2(ytd['totals']['current']['revenueWithVat'])
    top10 = customers[:10]
    top50_revenue = sum(round2(c.get('revenueWithVat')) for c in customers)
    top10_revenue = sum(round2(c.get('revenueWithVat')) for c in top10)
    top50_orders = sum(int(c.get('orders') or 0) for c in customers)
    repeat_heavy = [c for c in customers if int(c.get('orders') or 0) >= 20]

    segmented = []
    for c in top10:
        orders = int(c.get('orders') or 0)
        if orders >= 100:
            segment = 'whale'
        elif orders >= 40:
            segment = 'core_repeat'
        else:
            segment = 'vip_repeat'
        segmented.append({
            **c,
            'segment': segment,
        })

    return {
        'readiness': {
            'status': 'partial',
            'label': 'Customer fact is available as a high-value repeat-customer layer, not yet as a full customer universe.',
            'nextUnlock': 'Full order-history export with first confirmed purchase date per customer.',
        },
        'coverage': {
            'customersCount': total_customers,
            'ordersProcessed': total_orders,
            'top50RevenueSharePctOfYtd': round(top50_revenue / total_revenue * 100, 2) if total_revenue else None,
            'top10RevenueSharePctOfYtd': round(top10_revenue / total_revenue * 100, 2) if total_revenue else None,
            'top50OrdersSharePctOfProcessed': round(top50_orders / total_orders * 100, 2) if total_orders else None,
        },
        'repeatSignals': {
            'heavyRepeatCustomersInTop50': len(repeat_heavy),
            'top50AverageOrders': round(sum(int(c.get('orders') or 0) for c in customers) / len(customers), 2) if customers else 0,
            'top50AverageOrderValue': round(sum(round2(c.get('averageOrderValue')) for c in customers) / len(customers), 2) if customers else 0,
        },
        'estimatedNewVsReturning': {
            'status': 'proxy_only',
            'returningBaseStrength': 'high' if len(repeat_heavy) >= 20 else 'medium',
            'label': 'Repeat customer base is clearly material, but true new-vs-returning revenue still requires full-customer order history.',
        },
        'topCustomers': segmented,
    }


def build_order_quality(previous_day_summary: dict) -> dict:
    orders = int(previous_day_summary.get('orders') or 0)
    cancelled = int(previous_day_summary.get('cancelledOrders') or 0)
    problematic = int(previous_day_summary.get('problematicOrders') or 0)
    revenue = round2(previous_day_summary.get('revenueWithVat'))
    cancelled_rate = round(cancelled / orders * 100, 2) if orders else 0
    problematic_rate = round(problematic / orders * 100, 2) if orders else 0
    estimated_net = round(revenue * max(0, 1 - cancelled_rate / 100), 2)
    return {
        'orders': orders,
        'cancelledOrders': cancelled,
        'problematicOrders': problematic,
        'cancelledRatePct': cancelled_rate,
        'problematicRatePct': problematic_rate,
        'estimatedNetRevenueAfterCancellations': estimated_net,
        'qualityLabel': 'watch' if problematic_rate > 5 or cancelled_rate > 3 else 'healthy',
    }


def build_contribution_truth(finance_prev: dict, media_spend: float, order_quality: dict) -> dict:
    revenue = round2(finance_prev.get('revenue'))
    after_marketing = round2(finance_prev.get('afterMarketing'))
    operating = round2(finance_prev.get('operatingMargin'))
    profit = round2(finance_prev.get('profit'))
    return {
        'previousMonth': {
            'revenue': revenue,
            'grossMargin': round2(finance_prev.get('grossMargin')),
            'afterMarketing': after_marketing,
            'operatingMargin': operating,
            'profit': profit,
            'afterMarketingPct': round(after_marketing / revenue * 100, 2) if revenue else None,
            'operatingMarginPct': round(operating / revenue * 100, 2) if revenue else None,
            'paidMediaSpend': round2(media_spend),
        },
        'latestOrderPulse': order_quality,
        'nettoContributionReadiness': {
            'status': 'foundation_ready',
            'label': 'Finance-level contribution is live. Order-level netto contribution still needs returns, refunds, and product margin enrichment.',
        },
    }
