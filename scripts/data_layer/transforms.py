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


def find_ga4_channel(channels: list[dict], names: list[str]) -> dict:
    wanted = {name.lower() for name in names}
    for row in channels or []:
        if str(row.get('channel', '')).lower() in wanted:
            return row
    return {}


def sum_ga4_channels(channels: list[dict], names: list[str]) -> dict:
    wanted = {name.lower() for name in names}
    matched = [row for row in (channels or []) if str(row.get('channel', '')).lower() in wanted]
    revenue = sum(round2(row.get('purchaseRevenue')) for row in matched)
    sessions = sum(round2(row.get('sessions')) for row in matched)
    purchases = sum(round2(row.get('ecommercePurchases')) for row in matched)
    return {
        'channel': ' + '.join(names),
        'purchaseRevenue': revenue,
        'sessions': sessions,
        'ecommercePurchases': purchases,
        'purchaseRatePct': round(purchases / sessions * 100, 2) if sessions else None,
        'revenuePerSession': round(revenue / sessions, 2) if sessions else None,
        'matchedChannels': [row.get('channel') for row in matched],
    }


def classify_bucket(name: str, platform: str = '') -> str:
    text = f"{platform} {name}".lower()
    if any(token in text for token in ['remarketing', 'rmk', 'rtg', 'drtg', 'rem_', 'rem ', 'obs']):
        return 'remarketing'
    if any(token in text for token in ['brand', 'kralovstvi-tiande', 'kralovstvi tiande', 'království', 'tiande brand']):
        return 'brand'
    if any(token in text for token in ['klaviyo', 'email', 'sms', 'flow', 'newsletter']):
        return 'retention'
    if any(token in text for token in ['prosp', 'lead', 'kviz', 'brožury', 'kurzkompas', 'competitor', 'competitors', 'new', 'naked']):
        return 'acquisition'
    if any(token in text for token in ['pmax', 'shopping', 'dsa', 'produkt', 'produkty', 'kategorie', 'catalog', 'katalog', 'zboží.cz', 'zbozi']):
        return 'harvesting'
    return 'other'


def normalize_search_type(name: str, platform: str = '') -> str:
    text = f"{platform} {name}".lower()
    if 'brand' in text or 'království' in text or 'kralovstvi' in text:
        return 'brand_search'
    if 'competitor' in text or 'competitors' in text:
        return 'competitor_search'
    if any(token in text for token in ['pmax', 'shopping', 'zboží.cz', 'zbozi', 'produkt', 'produkty', 'kategorie', 'catalog', 'katalog']):
        return 'shopping_or_pmax'
    if any(token in text for token in ['remarketing', 'rmk', 'rtg', 'drtg', 'obs']):
        return 'remarketing_search'
    if any(token in text for token in ['dsa']):
        return 'dsa_search'
    return 'generic_search'


def summarise_bucket(rows: list[dict], revenue_key: str = 'revenue') -> list[dict]:
    groups: dict[str, dict] = {}
    for row in rows:
        bucket = row['bucket']
        current = groups.setdefault(bucket, {'bucket': bucket, 'spend': 0, 'revenue': 0, 'campaigns': 0})
        current['spend'] += round2(row.get('spend'))
        current['revenue'] += round2(row.get(revenue_key))
        current['campaigns'] += 1
    ordered = []
    for bucket, row in groups.items():
        spend = round2(row['spend'])
        revenue = round2(row['revenue'])
        ordered.append({
            **row,
            'spend': spend,
            'revenue': revenue,
            'roas': round(revenue / spend, 2) if spend else None,
        })
    ordered.sort(key=lambda item: item['spend'], reverse=True)
    return ordered


def build_top_campaigns(meta: dict, google: dict, sklik: dict) -> list[dict]:
    rows = []
    for row in meta.get('campaignsPreviousMonth', []):
        name = row.get('campaignName') or 'Unnamed'
        rows.append({
            'platform': 'Meta Ads',
            'name': name,
            'spend': round2(row.get('spendCzk')),
            'revenue': round2(row.get('purchaseValueCzk')),
            'roas': row.get('roas'),
            'status': row.get('effectiveStatus') or row.get('status'),
            'risk': 'high' if (row.get('roas') or 0) < 10 else 'medium',
            'bucket': classify_bucket(name, 'meta'),
        })
    for row in google.get('campaignsPreviousMonth', []):
        name = row.get('campaignName') or 'Unnamed'
        rows.append({
            'platform': 'Google Ads',
            'name': name,
            'spend': round2(row.get('spendCzk')),
            'revenue': round2(row.get('conversionValueCzk')),
            'roas': row.get('roas'),
            'status': row.get('status'),
            'risk': 'high' if (row.get('roas') or 0) < 15 and round2(row.get('spendCzk')) > 1000 else 'medium',
            'bucket': classify_bucket(name, 'google'),
        })
    for row in sklik.get('campaignPerformancePreviousMonth', []):
        spend = round2(row.get('priceCzk'))
        revenue = round2(row.get('conversionValueCzk'))
        name = row.get('name') or 'Unnamed'
        rows.append({
            'platform': 'Sklik',
            'name': name,
            'spend': spend,
            'revenue': revenue,
            'roas': round(revenue / spend, 2) if spend else None,
            'status': row.get('status'),
            'risk': 'low',
            'bucket': classify_bucket(name, 'sklik'),
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


def build_customer_fact(top_customers: dict, ytd: dict, full_customer_fact: dict | None = None) -> dict:
    total_revenue = round2(ytd['totals']['current']['revenueWithVat'])

    if full_customer_fact:
        customers = full_customer_fact.get('customers', [])
        summary = full_customer_fact.get('summary', {})
        total_customers = int(full_customer_fact.get('customersCount') or len(customers))
        total_orders = int(full_customer_fact.get('ordersProcessed') or 0)
        top_customers_ranked = sorted(customers, key=lambda c: round2(c.get('revenueWithVat')), reverse=True)
        top10 = top_customers_ranked[:10]
        top50 = top_customers_ranked[:50]
        top50_revenue = sum(round2(c.get('revenueWithVat')) for c in top50)
        top10_revenue = sum(round2(c.get('revenueWithVat')) for c in top10)
        top50_orders = sum(int(c.get('orders') or 0) for c in top50)
        repeat_heavy = [c for c in top50 if int(c.get('orders') or 0) >= 20]
        new_customers = int(summary.get('newCustomers') or 0)
        returning_customers = int(summary.get('returningCustomers') or 0)
        repeat_revenue = round2(summary.get('repeatRevenueWithVat'))
        new_revenue = round2(summary.get('newRevenueWithVat'))

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

        total_classified_revenue = repeat_revenue + new_revenue
        return {
            'readiness': {
                'status': 'full_ytd_window',
                'label': 'Customer fact now runs on full YTD order history with first-order classification per customer.',
                'nextUnlock': 'Add final lifecycle state, returns, and refunds to move from gross customer truth to netto customer truth.',
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
                'top50AverageOrders': round(sum(int(c.get('orders') or 0) for c in top50) / len(top50), 2) if top50 else 0,
                'top50AverageOrderValue': round(sum(round2(c.get('averageOrderValue')) for c in top50) / len(top50), 2) if top50 else 0,
            },
            'estimatedNewVsReturning': {
                'status': 'measured_ytd',
                'returningBaseStrength': 'high' if returning_customers > new_customers else 'medium',
                'label': f"Returning customers generated {repeat_revenue} Kč vs {new_revenue} Kč from new customers in the measured YTD window.",
                'newCustomers': new_customers,
                'returningCustomers': returning_customers,
                'newRevenueWithVat': new_revenue,
                'returningRevenueWithVat': repeat_revenue,
                'returningRevenueSharePct': round(repeat_revenue / total_classified_revenue * 100, 2) if total_classified_revenue else None,
            },
            'topCustomers': segmented,
        }

    customers = top_customers.get('top50', [])
    total_customers = top_customers.get('customersCount', 0)
    total_orders = top_customers.get('ordersProcessed', 0)
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


def build_order_quality(previous_day_summary: dict, full_order_fact: dict | None = None) -> dict:
    if full_order_fact:
        summary = full_order_fact.get('summary', {})
        orders = int(summary.get('orders') or 0)
        cancelled = int(summary.get('cancelledOrders') or 0)
        problematic = int(summary.get('problematicOrders') or 0)
        non_cancelled = int(summary.get('nonCancelledOrders') or 0)
        revenue = round2(summary.get('revenueWithVat'))
        cancelled_rate = round(cancelled / orders * 100, 2) if orders else 0
        problematic_rate = round(problematic / orders * 100, 2) if orders else 0
        estimated_net = round(revenue * max(0, 1 - cancelled_rate / 100), 2)
        return {
            'orders': orders,
            'nonCancelledOrders': non_cancelled,
            'cancelledOrders': cancelled,
            'problematicOrders': problematic,
            'cancelledRatePct': cancelled_rate,
            'problematicRatePct': problematic_rate,
            'estimatedNetRevenueAfterCancellations': estimated_net,
            'grossRevenueWithVat': revenue,
            'qualityLabel': 'watch' if problematic_rate > 5 or cancelled_rate > 3 else 'healthy',
            'window': full_order_fact.get('window'),
        }

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


def build_contribution_truth(finance_prev: dict, media_spend: float, order_quality: dict, klaviyo_prev: dict | None = None) -> dict:
    revenue = round2(finance_prev.get('revenue'))
    after_marketing = round2(finance_prev.get('afterMarketing'))
    operating = round2(finance_prev.get('operatingMargin'))
    profit = round2(finance_prev.get('profit'))
    retention_revenue = round2((klaviyo_prev or {}).get('totalAttributedRevenueCzk'))
    retention_orders = int((klaviyo_prev or {}).get('totalAttributedOrders') or 0)
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
            'retentionRevenueProxy': retention_revenue,
            'retentionOrdersProxy': retention_orders,
        },
        'latestOrderPulse': order_quality,
        'nettoContributionReadiness': {
            'status': 'foundation_ready',
            'label': 'Finance-level contribution is live. Order-level netto contribution still needs returns, refunds, and product margin enrichment.',
        },
    }


def build_paid_mix(meta: dict, google: dict, sklik: dict, klaviyo: dict) -> dict:
    campaign_rows = []

    for row in meta.get('campaignsPreviousMonth', []):
        name = row.get('campaignName') or 'Unnamed'
        campaign_rows.append({
            'platform': 'Meta Ads',
            'name': name,
            'bucket': classify_bucket(name, 'meta'),
            'spend': round2(row.get('spendCzk')),
            'revenue': round2(row.get('purchaseValueCzk')),
            'status': row.get('effectiveStatus') or row.get('status'),
        })
    for row in google.get('campaignsPreviousMonth', []):
        name = row.get('campaignName') or 'Unnamed'
        campaign_rows.append({
            'platform': 'Google Ads',
            'name': name,
            'bucket': classify_bucket(name, 'google'),
            'spend': round2(row.get('spendCzk')),
            'revenue': round2(row.get('conversionValueCzk')),
            'status': row.get('status'),
        })
    for row in sklik.get('campaignPerformancePreviousMonth', []):
        name = row.get('name') or 'Unnamed'
        campaign_rows.append({
            'platform': 'Sklik',
            'name': name,
            'bucket': classify_bucket(name, 'sklik'),
            'spend': round2(row.get('priceCzk')),
            'revenue': round2(row.get('conversionValueCzk')),
            'status': row.get('status'),
        })

    bucket_summary = summarise_bucket(campaign_rows)
    bucket_summary.append({
        'bucket': 'retention',
        'spend': 0,
        'revenue': round2(klaviyo['previousMonth']['totalAttributedRevenueCzk']),
        'campaigns': len(klaviyo.get('flowsPreviousMonth') or []),
        'roas': None,
    })
    bucket_summary.sort(key=lambda item: item['revenue'], reverse=True)

    return {
        'bucketSummaryPreviousMonth': bucket_summary,
        'topCampaigns': sorted(campaign_rows, key=lambda item: item['spend'], reverse=True)[:20],
        'decisionRules': {
            'acquisition': 'scale only when it creates measured net-new demand',
            'remarketing': 'protect efficiency, but do not count it as net-new growth',
            'retention': 'measure separately as owned repeat engine',
            'brand': 'treat as demand capture, not proof of incremental growth',
            'harvesting': 'optimize for capture efficiency, not for false acquisition claims',
        },
    }


def build_search_taxonomy(google: dict, sklik: dict) -> dict:
    rows = []
    for row in google.get('campaignsPreviousMonth', []):
        spend = round2(row.get('spendCzk'))
        revenue = round2(row.get('conversionValueCzk'))
        if spend <= 0 and revenue <= 0:
            continue
        name = row.get('campaignName') or 'Unnamed'
        rows.append({
            'platform': 'Google Ads',
            'name': name,
            'type': normalize_search_type(name, 'google'),
            'bucket': classify_bucket(name, 'google'),
            'spend': spend,
            'revenue': revenue,
        })
    for row in sklik.get('campaignPerformancePreviousMonth', []):
        spend = round2(row.get('priceCzk'))
        revenue = round2(row.get('conversionValueCzk'))
        if spend <= 0 and revenue <= 0:
            continue
        name = row.get('name') or 'Unnamed'
        rows.append({
            'platform': 'Sklik',
            'name': name,
            'type': normalize_search_type(name, 'sklik'),
            'bucket': classify_bucket(name, 'sklik'),
            'spend': spend,
            'revenue': revenue,
        })

    grouped: dict[str, dict] = {}
    for row in rows:
        current = grouped.setdefault(row['type'], {'type': row['type'], 'spend': 0, 'revenue': 0, 'campaigns': 0, 'platforms': set()})
        current['spend'] += row['spend']
        current['revenue'] += row['revenue']
        current['campaigns'] += 1
        current['platforms'].add(row['platform'])

    summary = []
    for row in grouped.values():
        spend = round2(row['spend'])
        revenue = round2(row['revenue'])
        summary.append({
            'type': row['type'],
            'spend': spend,
            'revenue': revenue,
            'roas': round(revenue / spend, 2) if spend else None,
            'campaigns': row['campaigns'],
            'platforms': sorted(row['platforms']),
        })
    summary.sort(key=lambda item: item['spend'], reverse=True)

    return {
        'summaryPreviousMonth': summary,
        'campaigns': sorted(rows, key=lambda item: item['spend'], reverse=True)[:25],
    }


def build_channel_intelligence(meta: dict, google: dict, sklik: dict, klaviyo: dict, ga4_channels: list[dict]) -> dict:
    paid_search_bundle = sum_ga4_channels(ga4_channels, ['Paid Search', 'Cross-network', 'Paid Shopping', 'Paid Other'])
    paid_social = find_ga4_channel(ga4_channels, ['Paid Social'])
    email = find_ga4_channel(ga4_channels, ['Email'])
    unassigned = find_ga4_channel(ga4_channels, ['Unassigned'])

    rows = [
        {
            'channel': 'Meta Ads',
            'bucket': 'paid_social',
            'decisionRole': 'acquisition_and_remarketing_mixed',
            'spendPreviousMonth': round2(meta['previousMonth']['spendCzk']),
            'platformRevenuePreviousMonth': round2(meta['previousMonth']['purchaseValueCzk']),
            'platformRoasPreviousMonth': meta['previousMonth']['roas'],
            'ga4ObservedRevenue': round2(paid_social.get('purchaseRevenue')),
            'ga4ObservedSessions': round2(paid_social.get('sessions')),
            'ga4ObservedPurchaseRatePct': paid_social.get('purchaseRatePct'),
            'ga4ObservedRoas': round(round2(paid_social.get('purchaseRevenue')) / round2(meta['previousMonth']['spendCzk']), 2) if round2(meta['previousMonth']['spendCzk']) else None,
            'trustScore': 30,
            'trustLabel': 'low',
            'primaryIssue': 'Platform claim is much stronger than observed paid social signal.',
            'nextQuestion': 'What is true prospecting contribution after exclusions and post-view inflation are removed?',
        },
        {
            'channel': 'Google Ads',
            'bucket': 'paid_search_bundle',
            'decisionRole': 'demand_harvesting_plus_brand',
            'spendPreviousMonth': round2(google['previousMonth']['spendCzk']),
            'platformRevenuePreviousMonth': round2(google['previousMonth']['conversionValueCzk']),
            'platformRoasPreviousMonth': google['previousMonth']['roas'],
            'ga4ObservedRevenue': paid_search_bundle.get('purchaseRevenue'),
            'ga4ObservedSessions': paid_search_bundle.get('sessions'),
            'ga4ObservedPurchaseRatePct': paid_search_bundle.get('purchaseRatePct'),
            'ga4ObservedRoas': round(paid_search_bundle.get('purchaseRevenue', 0) / round2(google['previousMonth']['spendCzk']), 2) if round2(google['previousMonth']['spendCzk']) else None,
            'trustScore': 62,
            'trustLabel': 'medium',
            'primaryIssue': 'Search works, but brand and remarketing are mixed into the same success story.',
            'nextQuestion': 'How much non-brand and net-new demand is left after separating brand, PMAX, and remarketing?',
        },
        {
            'channel': 'Sklik',
            'bucket': 'paid_search_secondary',
            'decisionRole': 'harvesting_unknown',
            'spendPreviousMonth': round2(sklik['previousMonth']['total']['priceCzk']),
            'platformRevenuePreviousMonth': round2(sklik['previousMonth']['total']['conversionValueCzk']),
            'platformRoasPreviousMonth': round(round2(sklik['previousMonth']['total']['conversionValueCzk']) / round2(sklik['previousMonth']['total']['priceCzk']), 2) if round2(sklik['previousMonth']['total']['priceCzk']) else None,
            'ga4ObservedRevenue': paid_search_bundle.get('purchaseRevenue'),
            'ga4ObservedSessions': paid_search_bundle.get('sessions'),
            'ga4ObservedPurchaseRatePct': paid_search_bundle.get('purchaseRatePct'),
            'ga4ObservedRoas': round(paid_search_bundle.get('purchaseRevenue', 0) / round2(sklik['previousMonth']['total']['priceCzk']), 2) if round2(sklik['previousMonth']['total']['priceCzk']) else None,
            'trustScore': 25,
            'trustLabel': 'low',
            'primaryIssue': 'Sklik reports extreme ROAS, but backend validation layer is still missing.',
            'nextQuestion': 'Is Sklik incremental, or mostly capturing branded and already-warm demand?',
        },
        {
            'channel': 'Klaviyo',
            'bucket': 'owned_retention',
            'decisionRole': 'retention',
            'spendPreviousMonth': 0,
            'platformRevenuePreviousMonth': round2(klaviyo['previousMonth']['totalAttributedRevenueCzk']),
            'platformRoasPreviousMonth': None,
            'ga4ObservedRevenue': round2(email.get('purchaseRevenue')),
            'ga4ObservedSessions': round2(email.get('sessions')),
            'ga4ObservedPurchaseRatePct': email.get('purchaseRatePct'),
            'ga4ObservedRoas': None,
            'trustScore': 68,
            'trustLabel': 'medium_high',
            'primaryIssue': 'Retention is clearly material, but still not reconciled to backend net revenue.',
            'nextQuestion': 'How much of repeat revenue is driven by lifecycle automation versus natural reorder behavior?',
        },
    ]

    rows.sort(key=lambda item: item['platformRevenuePreviousMonth'], reverse=True)
    return {
        'observationWindow': {
            'platform': 'previous_full_month',
            'analytics': 'last_7_days_or_current_focus_when_available',
            'warning': 'Platform and GA4 windows are directionally useful, not perfectly comparable yet.',
        },
        'rows': rows,
        'ga4Unassigned': {
            'revenue': round2(unassigned.get('purchaseRevenue')),
            'sessions': round2(unassigned.get('sessions')),
            'purchaseRatePct': unassigned.get('purchaseRatePct'),
        },
    }


def build_measurement_truth(meta: dict, google: dict, sklik: dict, klaviyo: dict, ga4: dict, finance_prev: dict, focus_channels: list[dict]) -> dict:
    paid_observed = sum_ga4_channels(focus_channels, ['Paid Search', 'Cross-network', 'Paid Shopping', 'Paid Other', 'Paid Social'])
    unassigned = find_ga4_channel(focus_channels, ['Unassigned'])
    platform_claimed = round2(meta['previousMonth']['purchaseValueCzk']) + round2(google['previousMonth']['conversionValueCzk']) + round2(sklik['previousMonth']['total']['conversionValueCzk']) + round2(klaviyo['previousMonth']['totalAttributedRevenueCzk'])
    finance_revenue = round2(finance_prev.get('revenue'))
    ga4_revenue = round2(ga4['previousMonth']['purchaseRevenue'])
    return {
        'sourceReadiness': [
            {'source': 'Finance', 'status': 'live', 'confidence': 'high'},
            {'source': 'GA4', 'status': 'live', 'confidence': 'medium'},
            {'source': 'Meta Ads', 'status': 'live', 'confidence': 'low'},
            {'source': 'Google Ads', 'status': 'live', 'confidence': 'medium'},
            {'source': 'Sklik', 'status': 'live', 'confidence': 'low'},
            {'source': 'Klaviyo', 'status': 'live', 'confidence': 'medium'},
            {'source': 'Customer fact YTD', 'status': 'live', 'confidence': 'high'},
            {'source': 'Order fact YTD', 'status': 'live', 'confidence': 'medium_high'},
        ],
        'reconciliation': {
            'financeRevenuePreviousMonth': finance_revenue,
            'ga4ObservedRevenuePreviousMonth': ga4_revenue,
            'platformClaimedRevenuePreviousMonth': platform_claimed,
            'ga4VsFinanceGapPct': pct_change(ga4_revenue, finance_revenue),
            'platformClaimsVsFinanceGapPct': pct_change(platform_claimed, finance_revenue),
            'paidObservedRevenueFocusWindow': paid_observed['purchaseRevenue'],
            'unassignedRevenueFocusWindow': round2(unassigned.get('purchaseRevenue')),
            'unassignedRevenueSharePctOfFocusObserved': round(round2(unassigned.get('purchaseRevenue')) / round2(ga4['last7days']['purchaseRevenue']) * 100, 2) if round2(ga4['last7days']['purchaseRevenue']) else None,
        },
        'headline': 'Measurement layer is now strong on finance and YTD customer truth, but still weaker on channel reconciliation and netto contribution.',
        'warnings': [
            'Platform-attributed revenue sums above finance revenue, so channel claims cannot be read as additive truth.',
            'GA4 still carries meaningful Unassigned revenue, which weakens channel decisioning.',
            'Paid search bundle is directionally useful, but Google and Sklik are not yet separated in backend truth.',
            'Netto truth still needs returns, refunds, and margin joins.',
        ],
    }


def build_acquisition_truth(customer_fact: dict, ga4: dict, klaviyo: dict, finance_prev: dict, channel_intelligence: dict, paid_mix: dict, search_taxonomy: dict) -> dict:
    paid_search = sum_ga4_channels(ga4.get('channelPerformance7d', []), ['Paid Search', 'Cross-network', 'Paid Shopping', 'Paid Other'])
    paid_social = find_ga4_channel(ga4.get('channelPerformance7d', []), ['Paid Social'])
    email = find_ga4_channel(ga4.get('channelPerformance7d', []), ['Email'])
    organic_search = find_ga4_channel(ga4.get('channelPerformance7d', []), ['Organic Search'])
    direct = find_ga4_channel(ga4.get('channelPerformance7d', []), ['Direct'])
    returning_share = customer_fact['estimatedNewVsReturning'].get('returningRevenueSharePct')
    return {
        'headline': 'Acquisition truth must be read through a repeat-heavy customer base, not through raw platform ROAS.',
        'customerBase': {
            'status': customer_fact['estimatedNewVsReturning']['status'],
            'returningRevenueSharePctYtd': returning_share,
            'newRevenueWithVatYtd': customer_fact['estimatedNewVsReturning'].get('newRevenueWithVat'),
            'returningRevenueWithVatYtd': customer_fact['estimatedNewVsReturning'].get('returningRevenueWithVat'),
        },
        'observedDemandMixLast7d': [
            {'channel': 'Paid Search bundle', 'revenue': paid_search.get('purchaseRevenue'), 'sessions': paid_search.get('sessions')},
            {'channel': 'Paid Social', 'revenue': round2(paid_social.get('purchaseRevenue')), 'sessions': round2(paid_social.get('sessions'))},
            {'channel': 'Email', 'revenue': round2(email.get('purchaseRevenue')), 'sessions': round2(email.get('sessions'))},
            {'channel': 'Organic Search', 'revenue': round2(organic_search.get('purchaseRevenue')), 'sessions': round2(organic_search.get('sessions'))},
            {'channel': 'Direct', 'revenue': round2(direct.get('purchaseRevenue')), 'sessions': round2(direct.get('sessions'))},
        ],
        'retentionProxy': {
            'klaviyoRevenuePreviousMonth': round2(klaviyo['previousMonth']['totalAttributedRevenueCzk']),
            'klaviyoOrdersPreviousMonth': int(klaviyo['previousMonth']['totalAttributedOrders'] or 0),
            'shareOfFinanceRevenuePct': round(round2(klaviyo['previousMonth']['totalAttributedRevenueCzk']) / round2(finance_prev.get('revenue')) * 100, 2) if round2(finance_prev.get('revenue')) else None,
        },
        'paidMixPreviousMonth': paid_mix['bucketSummaryPreviousMonth'],
        'searchTaxonomyPreviousMonth': search_taxonomy['summaryPreviousMonth'],
        'channelQuestions': [row['nextQuestion'] for row in channel_intelligence['rows']],
        'keyInterpretation': [
            'Paid acquisition cannot be judged without separating demand capture from true net-new creation.',
            'Repeat and owned channels already carry a very large share of real revenue.',
            'This means scaling paid channels should be gated by new-customer truth, not only by attributed ROAS.',
        ],
    }


def build_action_plan(customer_fact: dict, order_fact_ready: bool, measurement_truth: dict) -> dict:
    return {
        'headline': 'What to build next so the product gets close to or better than Roivenue.',
        'now': [
            'Separate acquisition, remarketing, retention, and brand into explicit channel buckets and decision rules.',
            'Add channel intelligence dataset to the UI homepage and management view so trust and ambiguity are visible on first load.',
            'Normalize campaign naming and map Google plus Sklik into a shared search taxonomy.',
        ],
        'next_2_to_4_weeks': [
            'Join returns, refunds, and final order lifecycle to order_fact so contribution becomes netto, not gross.',
            'Add margin enrichment per order or per product family to move from revenue truth to profit truth.',
            'Build backend-validated channel reconciliation so platform claims are compared against finance and order truth on the same window.',
        ],
        'then': [
            'Add creative and audience drilldown with acquisition versus remarketing split.',
            'Add anomaly detection and recommended action cards for spend spikes, conversion drops, and source outages.',
            'Add agency-review export that clearly separates facts, interpretation, and requested actions.',
        ],
        'currentState': {
            'customerTruth': customer_fact['readiness']['status'],
            'orderTruth': 'full_ytd_window' if order_fact_ready else 'partial',
            'measurementHeadline': measurement_truth['headline'],
        },
    }
