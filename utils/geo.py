"""Geographical utilities including the Haversine distance formula."""

import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in meters.
    Uses the Haversine formula with Earth's radius = 6371000 meters.
    """
    r = 6371000.0  # Earth's radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return r * c


def format_distance(meters: float) -> str:
    """Format distance into human-friendly string (meters or kilometers)."""
    if meters < 1000:
        return f"{round(meters)} m"
    return f"{meters / 1000.0:.2f} km"
