"""Tests for Haversine distance calculations and distance formatting."""

import math
from utils.geo import format_distance, haversine_distance


def test_haversine_same_point():
    """Distance between identical coordinates should be 0."""
    dist = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
    assert math.isclose(dist, 0.0, abs_tol=1e-5)


def test_haversine_known_coordinates():
    """
    Test distance between Statue of Liberty (40.6892, -74.0445)
    and Empire State Building (40.7484, -73.9857).
    Known approximate distance is ~8.2 km (8200 meters).
    """
    dist = haversine_distance(40.6892, -74.0445, 40.7484, -73.9857)
    assert 8100 < dist < 8400  # meters


def test_haversine_short_walk():
    """
    Test a short 100m walk delta (~0.0009 degrees latitude).
    """
    lat1, lon1 = 37.7749, -122.4194
    # Move ~111 meters north
    lat2, lon2 = 37.7759, -122.4194
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    assert 105 < dist < 115


def test_format_distance():
    """Verify distance formatting for meters and kilometers."""
    assert format_distance(450) == "450 m"
    assert format_distance(999) == "999 m"
    assert format_distance(1000) == "1.00 km"
    assert format_distance(1456) == "1.46 km"
