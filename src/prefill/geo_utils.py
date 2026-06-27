"""Utilitários geoespaciais leves para pré-preenchimento (sem PostGIS)."""

from __future__ import annotations

import math
from typing import Any


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em km entre dois pontos WGS84."""
    radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _ring_area_deg2(ring: list[list[float]]) -> float:
    area = 0.0
    for i in range(len(ring) - 1):
        lon1, lat1 = ring[i]
        lon2, lat2 = ring[i + 1]
        area += lon1 * lat2 - lon2 * lat1
    return abs(area) / 2.0


def polygon_area_ha(coordinates: list[list[list[float]]]) -> float:
    """Área aproximada em hectares (projeção simples; adequada para amostras locais)."""
    if not coordinates:
        return 0.0

    outer = coordinates[0]
    area_deg2 = _ring_area_deg2(outer)

    lat_sum = sum(point[1] for point in outer[:-1])
    lat_avg = lat_sum / max(len(outer) - 1, 1)
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * math.cos(math.radians(lat_avg))
    area_km2 = area_deg2 * km_per_deg_lat * km_per_deg_lon

    return round(area_km2 * 100, 2)


def geometry_centroid(geometry: dict[str, Any]) -> tuple[float, float]:
    """Centróide aproximado de LineString ou Polygon GeoJSON."""
    geom_type = geometry["type"]
    coords = geometry["coordinates"]

    if geom_type == "LineString":
        points = coords
    elif geom_type == "Polygon":
        points = coords[0]
    else:
        raise ValueError(f"Geometria não suportada: {geom_type}")

    lon_sum = sum(point[0] for point in points)
    lat_sum = sum(point[1] for point in points)
    count = len(points)

    return lat_sum / count, lon_sum / count


def feature_distance_km(feature: dict[str, Any], lat: float, lon: float) -> float:
    """Distância mínima em km do ponto ao centróide da feição."""
    centroid_lat, centroid_lon = geometry_centroid(feature["geometry"])
    return haversine_km(lat, lon, centroid_lat, centroid_lon)
