# Data Architecture

## Source groups

### Marketing platforms
- Meta Ads
- Google Ads
- Sklik
- future: Klaviyo / email, additional platforms

### Web analytics
- GA4
- future: first-party event pipeline / cookieless layer

### Backend / business systems
- e-shop orders
- product / category catalog
- returns / cancellations
- margin / finance logic
- customer dimension

## Core modeling layers

### 1. Raw connectors
Keep source-native data as close to original as possible.

### 2. Harmonization layer
Standardize fields such as:
- date
- country
- channel
- source / medium / campaign / adset / creative
- spend
- impressions
- clicks
- sessions
- orders
- revenue
- customer_id
- order_id

### 3. Business-truth layer
Apply:
- order deduplication
- refund / cancellation logic
- new vs returning classification
- margin enrichment
- country normalization
- campaign taxonomy cleanup

### 4. Decision layer
Expose metrics like:
- blended ROAS
- PNO
- contribution margin after marketing
- new customer revenue share
- attributed vs observed vs confirmed delta
- measurement confidence

## Key entities

### Channel performance fact
Grain:
- date x country x channel

### Campaign performance fact
Grain:
- date x platform x account x campaign

### Creative performance fact
Grain:
- date x platform x campaign x ad / creative

### Order fact
Grain:
- order_id

### Customer fact
Grain:
- customer_id

## Critical logic

### New vs returning
Rules need explicit definition, likely based on first confirmed purchase date, not platform claims.

### Attribution comparison
Maintain separate fields for:
- platform_reported_revenue
- analytics_observed_revenue
- backend_confirmed_revenue
- modeled_revenue

### Confidence scoring
Example inputs:
- presence of UTM / tags
- channel mapping quality
- platform / GA4 / backend gap
- campaign hygiene quality
- existence of audience contamination risk

## Output principle
The UI should never flatten all truth levels into one fake certainty number.

## Current implementation

The first live implementation now uses a multi-file data layer:

- `manifest.json` = routing and dataset registry
- `meta.json` = generation metadata and focus period
- `executive.json` = headline management KPIs
- `business-truth.json` = finance, cash, orders, customer sample
- `marketing-truth.json` = platform/channel truth and campaign layer
- `measurement.json` = observed GA4 and warning layer
- `audit-workspace.json` = campaign audit dataset
- `product-stage.json` = delivery stage and next steps

Build flow:
1. source snapshots are read from `reporting-v2/data/current`
2. `scripts/data_layer/sources.py` loads raw source files
3. `scripts/data_layer/transforms.py` handles shared transformations
4. `scripts/data_layer/builders.py` builds domain datasets
5. `scripts/build_snapshot.py` writes the final published data layer
