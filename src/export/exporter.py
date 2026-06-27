"""
Exportação de dados da propriedade em formatos abertos.

GeoJSON (RFC 7946) e XML simplificado compatível com fluxo SICAR Offline.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

from progress.progress_service import ProgressTracker

_DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "progress" / "retifications.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _feature_from_geometry(
    geometry: dict[str, Any],
    properties: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry,
    }


def export_to_geojson(property_data: dict[str, Any]) -> str:
    """
    Exporta dados da propriedade como FeatureCollection GeoJSON.

    Args:
        property_data: Dicionário com property_id, municipality, area_ha,
            geometry (opcional) e polygons (lista de {geometry, label, type}).
    """
    property_id = property_data.get("property_id", "unknown")
    features: list[dict[str, Any]] = []

    base_props = {
        "property_id": property_id,
        "municipality": property_data.get("municipality"),
        "area_ha": property_data.get("area_ha"),
        "exported_at": _utc_now_iso(),
        "source": "TerraPilot",
    }

    if geometry := property_data.get("geometry"):
        features.append(
            _feature_from_geometry(
                geometry,
                {**base_props, "feature_type": "property_boundary"},
            )
        )

    for index, polygon in enumerate(property_data.get("polygons", []), start=1):
        if "geometry" not in polygon:
            continue
        features.append(
            _feature_from_geometry(
                polygon["geometry"],
                {
                    **base_props,
                    "feature_type": polygon.get("type", "area"),
                    "label": polygon.get("label", f"area_{index}"),
                },
            )
        )

    collection = {
        "type": "FeatureCollection",
        "name": f"terrapilot_{property_id}",
        "features": features,
    }
    return json.dumps(collection, ensure_ascii=False, indent=2)


def export_to_sicar_xml(property_data: dict[str, Any]) -> str:
    """
    Exporta dados da propriedade em XML simplificado para importação no SICAR Offline.

    O formato segue estrutura hierárquica do CAR; campos obrigatórios do governo
    devem ser completados pelo produtor antes da submissão oficial.
    """
    root = Element("CAR")
    root.set("xmlns", "http://www.car.gov.br/schema")
    root.set("version", "1.0")
    root.set("generator", "TerraPilot")

    imovel = SubElement(root, "Imovel")
    SubElement(imovel, "CodigoImovel").text = str(
        property_data.get("property_id", "TERrapilot-EXPORT")
    )
    SubElement(imovel, "Municipio").text = str(property_data.get("municipality", ""))
    SubElement(imovel, "AreaTotalHa").text = str(property_data.get("area_ha", 0))
    SubElement(imovel, "DataExportacao").text = _utc_now_iso()

    if coords := property_data.get("centroid"):
        centroide = SubElement(imovel, "Centroide")
        SubElement(centroide, "Latitude").text = str(coords[0])
        SubElement(centroide, "Longitude").text = str(coords[1])

    areas = SubElement(imovel, "Areas")
    for polygon in property_data.get("polygons", []):
        area = SubElement(areas, "Area")
        SubElement(area, "Tipo").text = str(polygon.get("type", "DESCONHECIDO"))
        SubElement(area, "Nome").text = str(polygon.get("label", ""))
        geom = polygon.get("geometry", {})
        geo_elem = SubElement(area, "Geometria")
        SubElement(geo_elem, "Tipo").text = str(geom.get("type", "Polygon"))
        coords_elem = SubElement(geo_elem, "Coordenadas")
        coords_elem.text = json.dumps(geom.get("coordinates", []))

    if geometry := property_data.get("geometry"):
        perimetro = SubElement(imovel, "Perimetro")
        SubElement(perimetro, "Tipo").text = str(geometry.get("type", "Polygon"))
        SubElement(perimetro, "Coordenadas").text = json.dumps(
            geometry.get("coordinates", [])
        )

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root, encoding="unicode"
    )


def export_progress_report(
    property_id: str,
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Gera relatório de progresso das retificações para exportação ou impressão.

    Args:
        property_id: Identificador local do produtor/imóvel.
        db_path: Caminho opcional do SQLite de progresso.
    """
    tracker = ProgressTracker(db_path=db_path or _DEFAULT_DB_PATH)
    progress = tracker.get_progress(property_id)
    history = tracker.get_history(property_id)

    return {
        "property_id": property_id,
        "exported_at": _utc_now_iso(),
        "format": "terrapilot_progress_report",
        "summary": progress,
        "history": history,
        "human_message": progress["bar_message"],
        "is_complete": progress["is_complete"],
        "pending_issues": progress["pending_issue_codes"],
    }
