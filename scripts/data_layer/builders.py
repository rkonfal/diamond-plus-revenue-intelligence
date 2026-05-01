from __future__ import annotations

from .transforms import (
    build_acquisition_truth,
    build_action_plan,
    build_channel_intelligence,
    build_channel_truth,
    build_contribution_truth,
    build_customer_fact,
    build_measurement_truth,
    build_netto_contribution,
    build_order_quality,
    build_paid_mix,
    build_search_taxonomy,
    build_top_campaigns,
    pct_change,
    pick_focus_month,
    round2,
)


def build_data_layer(raw: dict) -> dict:
    meta = raw['meta']
    google = raw['google']
    ga4 = raw['ga4']
    sklik = raw['sklik']
    finance = raw['finance']
    marketing = raw['marketing']
    klaviyo = raw['klaviyo']
    portal = raw['portal']
    ytd = raw['eshopYtd']
    prev_day = raw['previousDayOrders']
    top_customers = raw['topCustomers']
    full_customer_fact = raw.get('customerFactYtdWindow')
    full_order_fact = raw.get('orderFactYtdWindow')

    ga4_focus, focus_key = pick_focus_month(ga4)
    ga4_previous = ga4['previousMonth']
    focus_channels = ga4.get('channelPerformanceCurrentMonth') or ga4.get('channelPerformance7d') or []
    top_campaigns = build_top_campaigns(meta, google, sklik)
    channel_truth = build_channel_truth(meta, google, sklik)
    focus_spend = round2(meta['previousMonth']['spendCzk'] + google['previousMonth']['spendCzk'] + sklik['previousMonth']['total']['priceCzk'])
    previous_day_summary = prev_day['summary']
    finance_prev = finance['previousMonth']
    finance_current = finance['currentMonth']
    customer_fact = build_customer_fact(top_customers, ytd, full_customer_fact)
    order_quality = build_order_quality(previous_day_summary, full_order_fact)
    contribution_truth = build_contribution_truth(finance_prev, focus_spend, order_quality, klaviyo.get('previousMonth'))
    netto_contribution = build_netto_contribution(finance_prev, order_quality, customer_fact, klaviyo.get('previousMonth'))
    channel_intelligence = build_channel_intelligence(meta, google, sklik, klaviyo, focus_channels)
    measurement_truth = build_measurement_truth(meta, google, sklik, klaviyo, ga4, finance_prev, focus_channels)
    paid_mix = build_paid_mix(meta, google, sklik, klaviyo)
    search_taxonomy = build_search_taxonomy(google, sklik)
    acquisition_truth = build_acquisition_truth(customer_fact, ga4, klaviyo, finance_prev, channel_intelligence, paid_mix, search_taxonomy)
    action_plan = build_action_plan(customer_fact, bool(full_order_fact), measurement_truth)

    meta_section = {
        'generatedAt': ga4.get('generatedAt'),
        'focus': {
            'mode': focus_key,
            'label': ga4_focus['label'],
            'dateFrom': ga4_focus['dateFrom'],
            'dateTo': ga4_focus['dateTo'],
        },
        'sourceStatus': {
            'portal': portal.get('marketing', {}),
            'finance': portal.get('finance', {}),
            'wpj': portal.get('wpJ', {}),
        },
    }

    executive = {
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
            'value': round(round2(ga4_focus['purchaseRevenue']) / focus_spend, 2) if focus_spend else None,
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
            'label': 'Medium',
            'reason': measurement_truth['headline'],
        },
        'newVsReturning': {
            'status': customer_fact['estimatedNewVsReturning']['status'],
            'label': customer_fact['estimatedNewVsReturning']['label'],
        },
        'reportNarrative': {
            'headline': 'Report už umí oddělit business truth, customer truth, acquisition truth a measurement truth, takže se dá řídit jako systém a ne jen číst jako dashboard.',
            'plainLanguage': [
                f"Za fokus období report vidí tržby {round2(ga4_focus['purchaseRevenue'])} Kč a spend {focus_spend} Kč.",
                f"Po marketingu vychází ve financích {round2(finance_prev['afterMarketing'])} Kč, takže byznys jako celek funguje.",
                customer_fact['estimatedNewVsReturning']['label'],
                'Nejslabší místo už není customer truth, ale channel reconciliation a netto contribution.',
            ],
            'whatToDoNow': action_plan['now'],
        },
    }

    business_truth = {
        'financePreviousMonth': finance_prev,
        'financeCurrentMonth': finance_current,
        'cash': finance['cash'],
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
        'historicalOrderWindow': full_order_fact.get('summary') if full_order_fact else None,
        'orderQuality': order_quality,
        'contributionTruth': contribution_truth,
        'nettoContribution': netto_contribution,
        'topCustomersSample': top_customers['top50'][:10],
    }

    marketing_truth = {
        'channels': channel_truth + [{
            'channel': 'Klaviyo',
            'spend': 0,
            'reportedRevenue': round2(klaviyo['previousMonth']['totalAttributedRevenueCzk']),
            'roas': None,
            'trust': 'medium',
            'notes': [
                'Retention / owned channel proxy',
                'Strong signal for returning customer revenue',
                'Should be separated from paid acquisition decisioning',
            ],
        }],
        'channelIntelligence': channel_intelligence,
        'paidMix': paid_mix,
        'searchTaxonomy': search_taxonomy,
        'ga4Channels': focus_channels,
        'marketingOverviewPreviousMonth': marketing['previousMonth'],
        'directSources': marketing['directSources'],
        'ownedRetention': klaviyo['previousMonth'],
        'topCampaigns': top_campaigns,
    }

    customer_truth = customer_fact

    order_fact = {
        'readiness': {
            'status': 'full_ytd_window' if full_order_fact else 'partial',
            'label': 'Order fact now covers the full measured YTD order window.' if full_order_fact else 'Order fact currently covers latest daily order pulse only, not the full historical order universe.',
            'nextUnlock': 'Add final lifecycle state, returns, refunds, and order-level margin joins.' if full_order_fact else 'Daily or monthly full order export with customer key and final lifecycle state.',
        },
        'latestDay': prev_day.get('items', []),
        'historicalWindow': full_order_fact.get('window') if full_order_fact else None,
        'historicalOrdersSample': (full_order_fact.get('orders') or [])[:100] if full_order_fact else [],
        'summary': order_quality,
    }

    measurement = {
        'ga4Channels': focus_channels,
        'landingPages': ga4['landingPages7d'],
        'topPages': ga4['topPages7d'],
        'countries': ga4['countries7d'],
        'truth': measurement_truth,
        'warnings': measurement_truth['warnings'],
        'nettoContribution': netto_contribution,
    }

    audit_workspace = {
        'topCampaigns': top_campaigns,
        'actions': action_plan['now'] + action_plan['next_2_to_4_weeks'],
        'nettoContributionWarnings': netto_contribution['warnings'],
    }

    final_truth_engine = {
        'status': 'operational_with_known_gaps',
        'headline': 'Final truth engine is now operational for finance truth, measured YTD customer truth, measured YTD order truth, and first decision-grade acquisition split. The main missing layer is netto contribution and backend channel reconciliation.',
        'whatIsTrulyKnown': [
            f"Finance after marketing: {round2(finance_prev['afterMarketing'])} Kč.",
            f"Net cash position: {round2(finance['cash']['netCashPosition'])} Kč.",
            customer_fact['estimatedNewVsReturning']['label'],
            f"Measured YTD orders processed: {customer_fact['coverage']['ordersProcessed']}",
        ],
        'whatIsEstimated': [
            'Channel incrementality is still confidence-led, not fully modeled.',
            'Platform channel truth is still non-additive and partially overlapping.',
            netto_contribution['readiness']['label'],
        ],
        'blockingMissingSources': [
            'Returns / refunds dataset tied to order_id.',
            'Order-level margin enrichment or product cost join.',
            'Backend validated channel attribution join on comparable time windows.',
        ],
    }

    role_views = {
        'management': {
            'headline': 'Byznys je silný, customer truth je měřený, ale marketing decisioning musí pořád procházet trust vrstvou a bucket split logikou.',
            'focus': [
                f"Po marketingu zůstalo {round2(finance_prev['afterMarketing'])} Kč.",
                f"Net cash pozice je {round2(finance['cash']['netCashPosition'])} Kč.",
                customer_fact['estimatedNewVsReturning']['label'],
            ],
            'questions': [
                'Které kanály skutečně vytváří nový demand?',
                'Kde je výkon reálný a kde je jen atribuční optimismus?',
                'Jak rychle dostaneme z gross truth netto truth?',
            ],
        },
        'marketing': {
            'headline': 'Marketing view už umí oddělit platform claim od observed truth a zároveň rozdělit spend na acquisition, remarketing, brand, retention a harvesting.',
            'focus': [
                channel_intelligence['rows'][0]['primaryIssue'],
                channel_intelligence['rows'][1]['primaryIssue'],
                'Retention a repeat revenue už nesmí být zaměňované za akviziční výkon.',
            ],
            'questions': [
                'Co škálovat, co omezit, co rozdělit na acquisition vs remarketing?',
                'Kde chybí tracking hygiena a naming disciplína?',
                'Kde je potřeba zpřísnit audience exclusions?',
            ],
        },
        'finance': {
            'headline': 'Finance view už stojí na byznys realitě, další krok je netto contribution po vratkách a marži.',
            'focus': [
                f"Revenue ve financích za minulý měsíc: {round2(finance_prev['revenue'])} Kč.",
                f"Operating margin: {round2(finance_prev['operatingMargin'])} Kč.",
                netto_contribution['readiness']['label'],
            ],
            'questions': [
                'Kolik z růstu je skutečně profitabilních po marketingu?',
                'Jak vypadá contribution po stornech, vratkách a marži?',
                'Jak rychle umíme odlišit růst obratu od růstu přínosu?',
            ],
        },
    }

    roivenue_comparison = {
        'headline': 'Roivenue comparison, where this product is already strong and where it is still behind.',
        'rows': [
            {'area': 'Business truth layer', 'ours': 'Strong finance, cash, order pulse and YTD truth connection', 'roivenue': 'Usually weaker on deeply custom internal ops context', 'status': 'strong'},
            {'area': 'Attribution / channel modeling', 'ours': 'Confidence-led and honest, but still not fully reconciled', 'roivenue': 'More mature and deeper by default', 'status': 'behind'},
            {'area': 'Customer truth', 'ours': 'Measured YTD new vs returning truth is now live', 'roivenue': 'Usually mature when fully integrated', 'status': 'close'},
            {'area': 'Readability for local team', 'ours': 'Much more tailored, plain-language, management-readable', 'roivenue': 'More standardized and polished', 'status': 'strong'},
            {'area': 'Automation and ownership', 'ours': 'Auto-refreshing and GitHub-native from canonical reporting pipeline', 'roivenue': 'More enterprise-ready workflow stack', 'status': 'close'},
            {'area': 'Netto contribution', 'ours': 'Estimated from measured order truth and finance ratios, but not yet fully joined by returns and SKU margin', 'roivenue': 'Often stronger once cost and attribution model is live', 'status': 'behind'},
            {'area': 'Fit to Diamond Plus', 'ours': 'Very high, custom-built around local business truth', 'roivenue': 'Generic platform fit', 'status': 'strong'},
        ],
        'summary': [
            'Compared with Roivenue, this product is already better aligned to Diamond Plus internal reality.',
            'It is now materially stronger on finance truth, customer truth, and management readability than before.',
            'The remaining gap is mainly channel reconciliation, netto contribution, and incrementality depth.',
        ],
    }

    product_stage = {
        'name': 'Stage 3, decision-grade revenue intelligence foundation',
        'done': [
            'Separate repo and product architecture',
            'Static-first live app scaffold',
            'Multi-file data layer fed from real reporting sources',
            'Backend truth blocks from finance and order pulse',
            'Customer fact YTD layer with measured first-order new vs returning classification',
            'Order fact YTD layer wired from canonical reporting pipeline',
            'Channel intelligence and measurement truth foundation',
            'Acquisition vs remarketing vs brand vs retention bucket split',
            'Unified Google plus Sklik search taxonomy layer',
            'Campaign audit workspace foundation',
        ],
        'next': [
            'Refund / return adjusted contribution logic per order',
            'Margin enrichment at order or product level',
            'Backend channel reconciliation on comparable windows',
            'Creative-level drilldown and operator workflows',
            'Anomaly detection and alert system',
        ],
    }

    return {
        'meta': meta_section,
        'executive': executive,
        'business-truth': business_truth,
        'marketing-truth': marketing_truth,
        'customer-truth': customer_truth,
        'order-fact': order_fact,
        'measurement': measurement,
        'audit-workspace': audit_workspace,
        'final-truth-engine': final_truth_engine,
        'role-views': role_views,
        'roivenue-comparison': roivenue_comparison,
        'product-stage': product_stage,
        'channel-intelligence': channel_intelligence,
        'acquisition-truth': acquisition_truth,
        'action-plan': action_plan,
        'netto-contribution': netto_contribution,
    }
