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


def build_customer_attribution_layer(readiness: dict | None, truth: dict | None, campaigns: dict | None) -> dict:
    readiness = readiness or {}
    truth = truth or {}
    campaigns = campaigns or {}
    summary = truth.get('summary') or {}
    campaign_rows = campaigns.get('campaigns') or []
    order_rows = truth.get('orders') or []
    return {
        'status': summary.get('status') or 'not_ready',
        'headline': 'Customer attribution vrstva ukazuje, které objednávky už umíme spárovat přes transactionId a jakou váhu dostávají kampaně v heuristice v1.',
        'window': truth.get('window') or readiness.get('window') or {},
        'metrics': {
            'ordersProcessed': summary.get('ordersProcessed') or summary.get('ordersInWindow') or 0,
            'ordersMatchedExactTransaction': summary.get('ordersMatchedExactTransaction') or 0,
            'ordersMatchedFallback': summary.get('ordersMatchedFallback') or 0,
            'ordersMatchedTotal': summary.get('ordersMatchedTotal') or summary.get('ordersMatchedExactTransaction') or 0,
            'ordersUnmatched': summary.get('ordersUnmatched') or 0,
            'matchRatePct': summary.get('matchRatePct') or 0,
            'weightedRevenueMatched': summary.get('weightedRevenueMatched') or 0,
        },
        'classification': summary.get('classification') or {},
        'topCampaigns': campaign_rows[:8],
        'recentOrders': order_rows[:6],
        'whyItMatters': [
            'Tady už nejde jen o platform claim, ale o konkrétní objednávky spárované přes transactionId.',
            'Každá spárovaná objednávka dostává rozdělení mezi introducer a closer podle heuristiky v1.',
            'Výstup je zatím částečný, ale už ukazuje, které kampaně mají vážený vliv na reálné nákupy.',
        ],
        'nextSteps': [
            'Rozšířit GA4 journey export z 30 dní na delší okno a doplnit další attribution pole.',
            'Doplnit identity stitching mimo transactionId, hlavně přes email hash nebo čas a hodnotu objednávky.',
            'Zpřesnit váhy pro brand, remarketing, retenci a direct do vlastního Diamond Plus modelu.',
        ],
        'readiness': readiness,
    }


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
    customer_attribution_truth = raw.get('customerAttributionTruth')
    campaign_customer_truth = raw.get('campaignCustomerTruth')
    customer_attribution_readiness = raw.get('customerAttributionReadiness')

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
    customer_attribution = build_customer_attribution_layer(customer_attribution_readiness, customer_attribution_truth, campaign_customer_truth)

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
            'label': 'Pozorované tržby v GA4',
        },
        'mediaSpend': {
            'value': focus_spend,
            'label': 'Placený spend napříč Meta, Google a Sklik',
        },
        'blendedRoas': {
            'value': round(round2(ga4_focus['purchaseRevenue']) / focus_spend, 2) if focus_spend else None,
            'label': 'Pozorované tržby / placený spend',
        },
        'grossMarginAfterMarketing': {
            'value': round2(finance_prev['afterMarketing']),
            'label': 'Finance po marketingu, poslední plný měsíc',
        },
        'netCashPosition': {
            'value': round2(finance['cash']['netCashPosition']),
            'label': 'Aktuální čistá hotovostní pozice',
        },
        'measurementConfidence': {
            'label': 'Střední',
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
            'label': 'Order fact teď pokrývá celé měřené YTD order okno.' if full_order_fact else 'Order fact zatím pokrývá jen poslední denní order pulse, ne celý historický order vesmír.',
            'nextUnlock': 'Doplnit finální lifecycle state, returns, refundy a order-level margin joiny.' if full_order_fact else 'Denní nebo měsíční full order export s customer key a finálním lifecycle state.',
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
        'customerAttributionTopCampaigns': customer_attribution['topCampaigns'],
    }

    final_truth_engine = {
        'status': 'operational_with_known_gaps',
        'headline': 'Final truth engine už běží pro finance truth, měřenou YTD customer truth, měřenou YTD order truth a první decision-grade akviziční split. Hlavní chybějící vrstva je netto contribution a backend channel reconciliation.',
        'whatIsTrulyKnown': [
            f"Finance po marketingu: {round2(finance_prev['afterMarketing'])} Kč.",
            f"Čistá hotovostní pozice: {round2(finance['cash']['netCashPosition'])} Kč.",
            customer_fact['estimatedNewVsReturning']['label'],
            f"Zpracované objednávky v měřeném YTD: {customer_fact['coverage']['ordersProcessed']}",
        ],
        'whatIsEstimated': [
            'Inkrementalita kanálů je zatím řízená confidence vrstvou, ne plně domodelovaná.',
            'Platform channel truth je stále neaditivní a částečně se překrývá.',
            netto_contribution['readiness']['label'],
        ],
        'blockingMissingSources': [
            'Dataset returns a refundů navázaný na order_id.',
            'Order-level margin enrichment nebo produktový cost join.',
            'Backend validovaný channel attribution join na srovnatelných časových oknech.',
        ],
        'customerAttributionStatus': customer_attribution['status'],
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
        'headline': 'Srovnání s Roivenue, kde je tenhle produkt už silný a kde ještě zaostává.',
        'rows': [
            {'area': 'Vrstva business truth', 'ours': 'Silné napojení na finance, cash, order pulse a YTD truth', 'roivenue': 'Obvykle slabší v hluboce custom interním kontextu', 'status': 'strong'},
            {'area': 'Atribuce a modelování kanálů', 'ours': 'Poctivé a confidence-led, ale ještě ne plně reconciled', 'roivenue': 'Standardně zralejší a hlubší', 'status': 'behind'},
            {'area': 'Customer truth', 'ours': 'Měřená YTD truth pro new vs returning už běží', 'roivenue': 'Obvykle zralé při plné integraci', 'status': 'close'},
            {'area': 'Čitelnost pro lokální tým', 'ours': 'Mnohem víc přizpůsobené, srozumitelné a management-friendly', 'roivenue': 'Více standardizované a uhlazené', 'status': 'strong'},
            {'area': 'Automatizace a vlastnictví', 'ours': 'Auto-refreshing a GitHub-native nad kanonickou reporting pipeline', 'roivenue': 'Enterprise-ready workflow stack', 'status': 'close'},
            {'area': 'Netto contribution', 'ours': 'Odhad z měřené order truth a finančních poměrů, ale ještě bez plného joinu vratek a SKU marže', 'roivenue': 'Často silnější po zapnutí cost a attribution modelu', 'status': 'behind'},
            {'area': 'Fit na Diamond Plus', 'ours': 'Velmi vysoký, stavěné přímo kolem lokální business truth', 'roivenue': 'Obecný platform fit', 'status': 'strong'},
        ],
        'summary': [
            'Oproti Roivenue je tenhle produkt už lépe sladěný s interní realitou Diamond Plus.',
            'Proti dřívějšku je teď výrazně silnější ve finance truth, customer truth a management čitelnosti.',
            'Zbývající mezera je hlavně v channel reconciliation, netto contribution a hloubce inkrementality.',
        ],
    }

    product_stage = {
        'name': 'Fáze 3, základ decision-grade revenue intelligence',
        'done': [
            'Separate repo and product architecture',
            'Static-first live app scaffold',
            'Multi-file data layer fed from real reporting sources',
            'Backend truth blocks from finance and order pulse',
            'Customer fact YTD layer with measured first-order new vs returning classification',
            'Order fact YTD layer wired from canonical reporting pipeline',
            'Základ channel intelligence a measurement truth',
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
        'customer-attribution': customer_attribution,
    }
