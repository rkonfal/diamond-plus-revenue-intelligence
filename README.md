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
- `app/` future dashboard app
- `data-contracts/` source mappings and schemas
- `notes/` working notes and research

## Current status

Project initialized on 2026-05-01 as a separate repository to keep it isolated from existing reporting and one-off audits.
