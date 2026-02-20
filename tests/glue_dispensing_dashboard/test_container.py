"""
Tests for GlueContainer — pure-Python dataclass, no Qt required.
"""
import pytest

from glue_dispensing_dashboard.core.container import GlueContainer
from glue_dispensing_dashboard.core.config import GlueDashboardConfig


@pytest.fixture
def container():
    return GlueContainer()


def test_default_config_is_glue_dashboard_config(container):
    assert isinstance(container.config, GlueDashboardConfig)


def test_get_cell_capacity_without_controller_returns_default(container):
    default = container.config.default_cell_capacity_grams
    assert container.get_cell_capacity(1) == default


def test_get_cell_initial_state_without_manager_returns_none(container):
    assert container.get_cell_initial_state(1) is None


def test_get_cell_glue_type_without_manager_returns_none(container):
    assert container.get_cell_glue_type(1) is None


def test_get_all_glue_types_without_manager_returns_empty(container):
    assert container.get_all_glue_types() == []


def test_controller_service_without_controller_returns_none(container):
    assert container.controller_service is None
