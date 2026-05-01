from __future__ import annotations

from .transforms import (
    build_channel_truth,
    build_contribution_truth,
    build_customer_fact,
    build_order_quality,
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
    portal = raw['portal']
    ytd = raw['eshopYtd']
    prev_day = raw['previousDayOrders']
    top_customers = raw['topCustomers']

    ga4_focus, focus_key = pick_focus_month(ga4)
    ga4_previous = ga4['previousMonth']
    focus_channels = ga4.get('channelPerformanceCurrentMonth') or ga4.get('channelPerformance7d') or []
    top_campaigns = build_top_campaigns(meta, google, sklik)
    channel_truth = build_channel_truth(meta, google, sklik)
    focus_spend = round2(meta['previousMonth']['spendCzk'] + google['previousMonth']['spendCzk'] + sklik['previousMonth']['total']['priceCzk'])
    previous_day_summary = prev_day['summary']
    finance_prev = finance['previousMonth']
    finance_current = finance['currentMonth']
    customer_fact = build_customer_fact(top_customers, ytd)
    order_quality = build_order_quality(previous_day_summary)
    contribution_truth = build_contribution_truth(finance_prev, focus_spend, order_quality)

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
            'label': 'Medium to low',
            'reason': 'Meta vs GA4 gap, high unattributed traffic, mixed acquisition logic, and incomplete customer classification.',
        },
        'newVsReturning': {
            'status': customer_fact['estimatedNewVsReturning']['status'],
            'label': customer_fact['estimatedNewVsReturning']['label'],
        },
        'reportNarrative': {
            'headline': 'Report ukazuje silný byznys, ale slabší jistotu v tom, které marketingové kanály růst opravdu vytváří.',
            'plainLanguage': [
                f"Za fokus období report vidí tržby {round2(ga4_focus['purchaseRevenue'])} Kč a spend {focus_spend} Kč.",
                f"Po marketingu vychází ve financích {round2(finance_prev['afterMarketing'])} Kč, takže byznys jako celek funguje.",
                f"Zákaznická báze má silný repeat signal, ale true new vs returning zatím není definitivní bez plné order historie.",
                'Platformy hlásí výkon lépe, než ho zatím umíme s vysokou jistotou potvrdit v analytice a backendu.',
            ],
            'whatToDoNow': [
                'Řídit rozpočet opatrněji podle channel trust vrstvy, ne jen podle platform ROAS.',
                'Dodělat plný order fact a customer fact model, aby byl new vs returning finální.',
                'Zavést order-level contribution po stornu, vratkách a marži.',
            ],
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
        'orderQuality': order_quality,
        'contributionTruth': contribution_truth,
        'topCustomersSample': top_customers['top50'][:10],
    }

    marketing_truth = {
        'channels': channel_truth,
        'ga4Channels': focus_channels,
        'marketingOverviewPreviousMonth': marketing['previousMonth'],
        'directSources': marketing['directSources'],
        'topCampaigns': top_campaigns,
    }

    customer_truth = customer_fact

    order_fact = {
        'readiness': {
            'status': 'partial',
            'label': 'Order fact currently covers latest daily order pulse only, not the full historical order universe.',
            'nextUnlock': 'Daily or monthly full order export with customer key and final lifecycle state.',
        },
        'latestDay': prev_day.get('items', []),
        'summary': order_quality,
    }

    measurement = {
        'ga4Channels': focus_channels,
        'landingPages': ga4['landingPages7d'],
        'topPages': ga4['topPages7d'],
        'countries': ga4['countries7d'],
        'warnings': [
            'High Unassigned share requires taxonomy and channel grouping cleanup.',
            'Paid Social in GA4 is materially weaker than Meta platform-reported revenue.',
            'Current model still needs backend customer fact logic for true new vs returning measurement.',
        ],
    }

    audit_workspace = {
        'topCampaigns': top_campaigns,
        'actions': [
            'Separate acquisition, remarketing, retention, and brand into explicit reporting layers.',
            'Build customer fact table with first confirmed purchase date to unlock true new-vs-returning classification.',
            'Introduce channel confidence scoring based on platform vs GA4 vs backend deltas.',
            'Tighten audience exclusions and tracking governance before trusting platform-reported growth.',
            'Use finance after-marketing and cash views as first-class management outputs, not side panels.',
        ],
    }

    role_views = {
        'management': {
            'headline': 'Byznys je profitabilní po marketingu, ale attribution jistota zatím zaostává za business výsledkem.',
            'focus': [
                f"Po marketingu zůstalo {round2(finance_prev['afterMarketing'])} Kč.",
                f"Net cash pozice je {round2(finance['cash']['netCashPosition'])} Kč.",
                customer_fact['estimatedNewVsReturning']['label'],
            ],
            'questions': [
                'Které kanály skutečně vytváří nový demand?',
                'Kde je výkon reálný a kde je jen atribuční optimismus?',
                'Jak moc je růst závislý na repeat zákaznících?',
            ],
        },
        'marketing': {
            'headline': 'Marketing view má sloužit k řízení spendu podle trust vrstvy, ne jen podle platform ROAS.',
            'focus': [
                'Meta má silný platform revenue, ale nízkou důvěru.',
                'Google drží nejsilnější výkon, ale je brand-heavy.',
                'Sklik potřebuje jasnější roli a validaci proti backendu.',
            ],
            'questions': [
                'Co škálovat, co omezit, co rozdělit na acquisition vs remarketing?',
                'Kde chybí tracking hygiena a naming disciplína?',
                'Kde je potřeba zpřísnit audience exclusions?',
            ],
        },
        'finance': {
            'headline': 'Finance view spojuje marketing spend s margin realitou, ne jen s obratem.',
            'focus': [
                f"Revenue ve financích za minulý měsíc: {round2(finance_prev['revenue'])} Kč.",
                f"Operating margin: {round2(finance_prev['operatingMargin'])} Kč.",
                contribution_truth['nettoContributionReadiness']['label'],
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
            {'area': 'Business truth layer', 'ours': 'Strong finance and order pulse connection', 'roivenue': 'Usually stronger attribution and channel modeling, weaker custom internal ops context', 'status': 'strong'},
            {'area': 'Attribution / channel modeling', 'ours': 'Partial, confidence-led, explicit about uncertainty', 'roivenue': 'More mature and deeper by default', 'status': 'behind'},
            {'area': 'Readability for local team', 'ours': 'Much more tailored, plain-language, management-readable', 'roivenue': 'More standardized and polished', 'status': 'strong'},
            {'area': 'Customer truth', 'ours': 'Proxy layer only so far', 'roivenue': 'Typically more mature when fully integrated', 'status': 'behind'},
            {'area': 'Automation and ownership', 'ours': 'Now auto-refreshing and GitHub-native', 'roivenue': 'More enterprise-ready workflow stack', 'status': 'close'},
            {'area': 'Fit to Diamond Plus', 'ours': 'Very high, custom-built around local business truth', 'roivenue': 'Generic platform fit', 'status': 'strong'},
        ],
        'summary': [
            'Compared with Roivenue, this product is already better aligned to Diamond Plus internal reality.',
            'It is not yet as mature in attribution depth, customer truth, and modeled contribution logic.',
            'If we finish the full order/customer truth engine, the product gets within sight of a genuinely competitive in-house alternative.',
        ],
    }

    product_stage = {
        'name': 'Stage 2, business truth and customer layer foundation',
        'done': [
            'Separate repo and product architecture',
            'Static-first live app scaffold',
            'Multi-file data layer fed from real reporting sources',
            'Backend truth blocks from finance and order pulse',
            'Customer fact proxy layer with repeat-customer concentration signals',
            'Campaign audit workspace foundation',
        ],
        'next': [
            'Full-customer order history for real new vs returning revenue',
            'Refund / return / cancellation adjusted contribution logic per order',
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
        'role-views': role_views,
        'roivenue-comparison': roivenue_comparison,
        'product-stage': product_stage,
    }
