# Diamond Plus Revenue Intelligence

Standalone project for building a revenue-intelligence layer for Diamond Plus, inspired by tools like Roivenue but tailored to our own stack, data quality, decision-making flow, and commercial needs.

## Goal

Build a management and channel-operator system that combines:
- ad platform data,
- GA4 / analytics data,
- backend / order / margin data,
- customer new vs returning logic,
- attribution and measurement confidence,
- actionable reporting.

The aim is not just to show dashboards, but to create a decision system.

## Core idea

This project should answer:
- What is really driving revenue?
- Which channels bring new customers vs. recycle existing demand?
- Where is reporting overstating contribution?
- What should be scaled, fixed, or cut right now?
- What is the true contribution after margins, returns, cancellations, and attribution uncertainty?

## Initial scope

### Phase 1
- unified metric layer
- executive homepage
- channel performance view
- new vs returning customer split
- measurement confidence / attribution warning layer
- audit-ready marketing view

### Phase 2
- product / category contribution view
- campaign and creative drilldown
- country split (CZ / SK / others)
- margin-aware marketing efficiency
- anomaly detection and alerts

### Phase 3
- modeled attribution layer
- media-mix / incrementality support
- operator workflows and recommendations
- exports back to ad platforms / external BI

## Repo structure

- `docs/` product, architecture, roadmap, metric definitions
- `assets/` frontend UI and browser-side data layer loader
- `data/` generated datasets for the live prototype
- `scripts/` build pipeline for the data layer
- `app/` legacy early scaffold

## Data layer

The prototype now has a real multi-file data layer instead of one flat payload.

Generated files:
- `data/manifest.json`
- `data/meta.json`
- `data/executive.json`
- `data/business-truth.json`
- `data/marketing-truth.json`
- `data/customer-truth.json`
- `data/order-fact.json`
- `data/measurement.json`
- `data/audit-workspace.json`
- `data/product-stage.json`

Build commands:
- local source: `python3 scripts/build_snapshot.py`
- synced source: `python3 scripts/sync_sources.py && REVENUE_SOURCE_DIR=source/current python3 scripts/build_snapshot.py`

Synced source strategy:
- `scripts/sync_sources.py` now compacts large optional fact datasets into lightweight local files:
  - `source/current/customer_fact_ytd_compact.json`
  - `source/current/order_fact_ytd_compact.json`
- the full heavy source files are not meant to live in this repo anymore
- `build_snapshot.py` can read compact versions first, then fall back to full files when available

## Automatic updates

The repo now includes `.github/workflows/auto-refresh.yml`.
It downloads fresh source files from `rkonfal/diamond-plus-reporting-preview`, compacts the heavy optional fact exports, rebuilds the data layer, and commits updates automatically on schedule.

## Current status

Project initialized on 2026-05-01 as a separate repository to keep it isolated from existing reporting and one-off audits.
It now includes a decision-grade data layer foundation for executive, business-truth, marketing-truth, customer-truth, acquisition-truth, channel-intelligence, netto-contribution, measurement, and audit views.
