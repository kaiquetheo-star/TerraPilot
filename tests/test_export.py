"""Testes do módulo de exportação (GeoJSON, SICAR XML, relatório de progresso)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from export.exporter import (  # noqa: E402
    export_progress_report,
    export_to_geojson,
    export_to_sicar_xml,
)
from progress.progress_service import ProgressTracker, clear_guide_metadata_cache  # noqa: E402


SAMPLE_PROPERTY = {
    "property_id": "raimundo_001",
    "municipality": "Santarém",
    "area_ha": 30.0,
    "centroid": [-2.4431, -54.7083],
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-54.71, -2.44],
                [-54.70, -2.44],
                [-54.70, -2.45],
                [-54.71, -2.45],
                [-54.71, -2.44],
            ]
        ],
    },
    "polygons": [
        {
            "type": "RL",
            "label": "Reserva Legal",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-54.705, -2.442],
                        [-54.703, -2.442],
                        [-54.703, -2.444],
                        [-54.705, -2.444],
                        [-54.705, -2.442],
                    ]
                ],
            },
        }
    ],
}


def test_export_to_geojson_valid_feature_collection():
    result = export_to_geojson(SAMPLE_PROPERTY)
    data = json.loads(result)

    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2
    assert data["features"][0]["properties"]["property_id"] == "raimundo_001"
    assert data["features"][0]["geometry"]["type"] == "Polygon"


def test_export_to_sicar_xml_contains_property_fields():
    xml = export_to_sicar_xml(SAMPLE_PROPERTY)

    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<CAR" in xml
    assert "<CodigoImovel>raimundo_001</CodigoImovel>" in xml
    assert "<Municipio>Santarém</Municipio>" in xml
    assert "<AreaTotalHa>30.0</AreaTotalHa>" in xml
    assert "<Tipo>RL</Tipo>" in xml


def test_export_progress_report(tmp_path):
    clear_guide_metadata_cache()
    db_path = tmp_path / "progress.db"
    tracker = ProgressTracker(db_path=db_path)
    tracker.register_issues("raimundo_001", ["APP_RIVER_WIDTH", "RL_PERIMETER_DIVERGENCE"])
    tracker.complete_issue("raimundo_001", "APP_RIVER_WIDTH")

    report = export_progress_report("raimundo_001", db_path=db_path)

    assert report["property_id"] == "raimundo_001"
    assert report["summary"]["resolved_count"] == 1
    assert report["summary"]["total_count"] == 2
    assert report["is_complete"] is False
    assert len(report["history"]) == 2
    clear_guide_metadata_cache()


def test_export_to_geojson_empty_polygons_still_exports_boundary():
    minimal = {
        "property_id": "demo",
        "geometry": SAMPLE_PROPERTY["geometry"],
    }
    data = json.loads(export_to_geojson(minimal))

    assert len(data["features"]) == 1
