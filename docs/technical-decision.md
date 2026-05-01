# Technical Decision

## Chosen first stack

For the first build, we are using a static-first architecture:
- plain HTML
- CSS
- lightweight browser-side JavaScript
- GitHub Pages deployment

## Why this is the right first step

- fastest path to a live preview
- easy to share internally
- no framework overhead before the data model is stable
- ideal for validating product direction and information architecture first

## Planned evolution

If the product direction proves right, the next likely step is:
- componentized frontend app
- typed data contracts
- scheduled snapshot generation or API-backed data layer
- backend business-truth layer for orders, customers, returns, margin, and attribution comparison

## Principle

First validate the revenue operating model.
Then scale the engineering complexity.
