"""
Tests for GlueDashboardAppWidget — Level 3 UI shell.
Requires a QApplication (provided by pytest-qt via the qtbot fixture).
"""
import pytest
from unittest.mock import MagicMock

from glue_dispensing_dashboard.app.GlueDashboardAppWidget import GlueDashboardAppWidget
from glue_dispensing_dashboard.adapter.GlueAdapter import GlueAdapter
from glue_dispensing_dashboard.core.config import GlueDashboardConfig


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def app_widget(qtbot):
    widget = GlueDashboardAppWidget(
        config=GlueDashboardConfig(),
        action_buttons=GlueAdapter.ACTION_BUTTONS,
        cards=[],
    )
    qtbot.addWidget(widget)
    return widget


# ------------------------------------------------------------------ #
#  Construction                                                        #
# ------------------------------------------------------------------ #

def test_builds_dashboard_internally(app_widget):
    assert hasattr(app_widget, "_dashboard")


def test_exposes_required_signals(app_widget):
    # These attributes must exist and be PyQt signals
    for name in ("start_requested", "stop_requested", "pause_requested",
                 "action_requested", "language_changed", "LOGOUT_REQUEST"):
        assert hasattr(app_widget, name)


# ------------------------------------------------------------------ #
#  Signal propagation                                                  #
# ------------------------------------------------------------------ #

def test_start_signal_propagates(app_widget, qtbot):
    with qtbot.waitSignal(app_widget.start_requested, timeout=500):
        app_widget._dashboard.start_requested.emit()


def test_stop_signal_propagates(app_widget, qtbot):
    with qtbot.waitSignal(app_widget.stop_requested, timeout=500):
        app_widget._dashboard.stop_requested.emit()


def test_pause_signal_propagates(app_widget, qtbot):
    with qtbot.waitSignal(app_widget.pause_requested, timeout=500):
        app_widget._dashboard.pause_requested.emit()


def test_action_signal_propagates(app_widget, qtbot):
    with qtbot.waitSignal(app_widget.action_requested, timeout=500) as blocker:
        app_widget._dashboard.action_requested.emit("reset_errors")
    assert blocker.args == ["reset_errors"]


# ------------------------------------------------------------------ #
#  Localization                                                        #
# ------------------------------------------------------------------ #

def test_retranslate_emits_language_changed(app_widget, qtbot):
    with qtbot.waitSignal(app_widget.language_changed, timeout=500):
        app_widget.retranslateUi()


# ------------------------------------------------------------------ #
#  Setter proxy API                                                    #
# ------------------------------------------------------------------ #

def test_set_cell_weight_delegates_to_dashboard(app_widget):
    app_widget._dashboard = MagicMock()
    app_widget.set_cell_weight(1, 2500.0)
    app_widget._dashboard.set_cell_weight.assert_called_once_with(1, 2500.0)


def test_set_cell_state_delegates_to_dashboard(app_widget):
    app_widget._dashboard = MagicMock()
    app_widget.set_cell_state(1, "ready")
    app_widget._dashboard.set_cell_state.assert_called_once_with(1, "ready")


def test_set_start_enabled_delegates_to_dashboard(app_widget):
    app_widget._dashboard = MagicMock()
    app_widget.set_start_enabled(True)
    app_widget._dashboard.set_start_enabled.assert_called_once_with(True)
