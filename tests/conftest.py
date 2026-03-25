"""
pytest configuration and shared fixtures for Sentinel Curator tests.
"""

import pytest


@pytest.fixture
def unclassified_role() -> str:
    return "UNCLASSIFIED"


@pytest.fixture
def restricted_role() -> str:
    return "RESTRICTED"


@pytest.fixture
def confidential_role() -> str:
    return "CONFIDENTIAL"
