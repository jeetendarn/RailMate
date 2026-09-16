import os

from providers.demo_provider import DemoRailwayProvider


def test_demo_provider_loads():
    provider = DemoRailwayProvider("data/trains.json")
    assert len(provider.trains) > 0


def test_demo_provider_search():
    provider = DemoRailwayProvider("data/trains.json")
    results = provider.search_trains("Mysore", "Chennai", "2026-09-21", "2A")
    assert isinstance(results, list)
