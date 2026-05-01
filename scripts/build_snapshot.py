#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from data_layer import build_data_layer
from data_layer.sources import SourceStore

ROOT = Path('/Users/rudolfkonfal/.openclaw/workspace/diamond-plus-revenue-intelligence')
SOURCE = Path('/Users/rudolfkonfal/.openclaw/workspace/reporting-v2/data/current')
OUTPUT_DIR = ROOT / 'data'


def write_json(path: Path, payload: dict):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = SourceStore(SOURCE).load_all()
    data_layer = build_data_layer(raw)

    manifest = {
        'generatedAt': data_layer['meta']['generatedAt'],
        'focus': data_layer['meta']['focus'],
        'datasets': {
            'meta': 'meta.json',
            'executive': 'executive.json',
            'businessTruth': 'business-truth.json',
            'marketingTruth': 'marketing-truth.json',
            'measurement': 'measurement.json',
            'auditWorkspace': 'audit-workspace.json',
            'productStage': 'product-stage.json',
        },
    }

    write_json(OUTPUT_DIR / 'meta.json', data_layer['meta'])
    write_json(OUTPUT_DIR / 'executive.json', data_layer['executive'])
    write_json(OUTPUT_DIR / 'business-truth.json', data_layer['business-truth'])
    write_json(OUTPUT_DIR / 'marketing-truth.json', data_layer['marketing-truth'])
    write_json(OUTPUT_DIR / 'measurement.json', data_layer['measurement'])
    write_json(OUTPUT_DIR / 'audit-workspace.json', data_layer['audit-workspace'])
    write_json(OUTPUT_DIR / 'product-stage.json', data_layer['product-stage'])
    write_json(OUTPUT_DIR / 'manifest.json', manifest)

    snapshot = {
        'generatedAt': data_layer['meta']['generatedAt'],
        'focus': data_layer['meta']['focus'],
        'executive': data_layer['executive'],
        'businessTruth': data_layer['business-truth'],
        'marketingTruth': data_layer['marketing-truth'],
        'measurement': data_layer['measurement'],
        'auditWorkspace': data_layer['audit-workspace'],
        'productStage': data_layer['product-stage'],
    }
    write_json(OUTPUT_DIR / 'revenue-intelligence-snapshot.json', snapshot)
    print(f'Wrote data layer to {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
