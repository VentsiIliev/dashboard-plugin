"""
Tests for ControlButtonsWidget — pure UI widget, no broker knowledge.
Requires a QApplication (provided by pytest-qt via the qtbot fixture).
"""
import pytest

from dashboard.widgets.ControlButtonsWidget import ControlButtonsWidget


# ------------------------------------------------------------------ #
#  Fixture                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def widget(qtbot):
    w = ControlButtonsWidget()
    qtbot.addWidget(w)
    return w


# ------------------------------------------------------------------ #
#  Initial state                                                       #
# ------------------------------------------------------------------ #

def test_buttons_disabled_by_default(widget):
    assert not widget.start_btn.isEnabled()
    assert not widget.stop_btn.isEnabled()
    assert not widget.pause_btn.isEnabled()


def test_initial_button_labels(widget):
    assert widget.start_btn.text() == "Start"
    assert widget.stop_btn.text() == "Stop"
    assert widget.pause_btn.text() == "Pause"


# ------------------------------------------------------------------ #
#  Signals                                                             #
# ------------------------------------------------------------------ #

def test_start_clicked_signal(widget, qtbot):
    widget.set_start_enabled(True)
    with qtbot.waitSignal(widget.start_clicked, timeout=500):
        widget.start_btn.click()


def test_stop_clicked_signal(widget, qtbot):
    widget.set_stop_enabled(True)
    with qtbot.waitSignal(widget.stop_clicked, timeout=500):
        widget.stop_btn.click()


def test_pause_clicked_signal(widget, qtbot):
    widget.set_pause_enabled(True)
    with qtbot.waitSignal(widget.pause_clicked, timeout=500):
        widget.pause_btn.click()


# ------------------------------------------------------------------ #
#  Setter API                                                          #
# ------------------------------------------------------------------ #

def test_set_start_enabled_true(widget):
    widget.set_start_enabled(True)
    assert widget.start_btn.isEnabled()


def test_set_start_enabled_false(widget):
    widget.set_start_enabled(True)
    widget.set_start_enabled(False)
    assert not widget.start_btn.isEnabled()


def test_set_stop_enabled(widget):
    widget.set_stop_enabled(True)
    assert widget.stop_btn.isEnabled()


def test_set_pause_enabled(widget):
    widget.set_pause_enabled(True)
    assert widget.pause_btn.isEnabled()


def test_set_pause_text(widget):
    widget.set_pause_text("Resume")
    assert widget.pause_btn.text() == "Resume"


# ------------------------------------------------------------------ #
#  Localization                                                        #
# ------------------------------------------------------------------ #

def test_retranslate_resets_button_labels(widget):
    widget.set_pause_text("Resume")
    widget.retranslateUi()
    assert widget.pause_btn.text() == "Pause"
    assert widget.start_btn.text() == "Start"
    assert widget.stop_btn.text() == "Stop"
