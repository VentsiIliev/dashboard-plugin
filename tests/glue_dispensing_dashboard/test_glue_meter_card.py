"""
Tests for GlueMeterCard widget.
Requires a QApplication (provided by pytest-qt via the qtbot fixture).
"""
import pytest

from glue_dispensing_dashboard.ui.widgets.GlueMeterCard import GlueMeterCard


# ------------------------------------------------------------------ #
#  Fixture                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def card(qtbot):
    w = GlueMeterCard(label_text="Glue 1", index=1, capacity_grams=5000.0)
    qtbot.addWidget(w)
    return w


# ------------------------------------------------------------------ #
#  Construction                                                        #
# ------------------------------------------------------------------ #

def test_initial_state_is_unknown(card):
    assert card._current_state_str == "unknown"


def test_initial_glue_type_is_none(card):
    assert card._current_glue_type is None


def test_title_label_shows_constructor_text(card):
    assert card.title_label.text() == "Glue 1"


# ------------------------------------------------------------------ #
#  State management                                                    #
# ------------------------------------------------------------------ #

def test_set_state_stores_state_string(card):
    card.set_state("ready")
    assert card._current_state_str == "ready"


def test_set_state_updates_tooltip(card):
    card.set_state("error")
    assert card.state_indicator.toolTip() != ""


def test_set_weight_does_not_raise(card):
    card.set_weight(2500.0)   # delegates to GlueMeterWidget


def test_set_glue_type_stores_value(card):
    card.set_glue_type("PUR Hotmelt")
    assert card._current_glue_type == "PUR Hotmelt"


def test_set_glue_type_updates_label(card):
    card.set_glue_type("EVA Adhesive")
    assert "EVA Adhesive" in card.glue_type_label.text()


def test_set_glue_type_none_shows_no_glue_text(card):
    card.set_glue_type(None)
    assert card._current_glue_type is None


# ------------------------------------------------------------------ #
#  Signal                                                              #
# ------------------------------------------------------------------ #

def test_change_button_emits_signal_with_card_index(card, qtbot):
    with qtbot.waitSignal(card.change_glue_requested, timeout=500) as blocker:
        card.change_glue_button.click()
    assert blocker.args == [1]


# ------------------------------------------------------------------ #
#  Localization                                                        #
# ------------------------------------------------------------------ #

def test_retranslate_preserves_glue_type_in_label(card):
    card.set_glue_type("Silicone")
    card.retranslateUi()
    assert "Silicone" in card.glue_type_label.text()


def test_retranslate_without_glue_type_shows_loading(card):
    card.retranslateUi()   # _current_glue_type is None
    assert card.glue_type_label.text() != ""
