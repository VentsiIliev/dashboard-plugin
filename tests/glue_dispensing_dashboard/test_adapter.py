"""
Tests for GlueAdapter — broker wiring, UI delegation, state management.
No Qt widget is instantiated; the UI is a MagicMock.
"""
import pytest
from unittest.mock import MagicMock, call

from external_dependencies.ApplicationState import ApplicationState
from external_dependencies.topics import GlueCellTopics, SystemTopics
from glue_dispensing_dashboard.adapter.GlueAdapter import GlueAdapter


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def mock_ui():
    ui = MagicMock()
    ui.get_card.return_value = MagicMock()
    return ui


@pytest.fixture
def mock_container():
    c = MagicMock()
    # Return None so _initialize_display() doesn't call UI setters
    c.get_cell_initial_state.return_value = None
    c.get_cell_glue_type.return_value = None
    return c


@pytest.fixture
def adapter(mock_ui, mock_container):
    a = GlueAdapter(mock_ui, mock_container)
    a.connect()
    yield a
    a.disconnect()


# ------------------------------------------------------------------ #
#  Subscription wiring                                                 #
# ------------------------------------------------------------------ #

def test_connect_subscribes_cell_weight_topics(clean_broker, adapter):
    for cell_id in [1, 2, 3]:
        assert clean_broker.get_subscriber_count(GlueCellTopics.cell_weight(cell_id)) == 1


def test_connect_subscribes_cell_state_topics(clean_broker, adapter):
    for cell_id in [1, 2, 3]:
        assert clean_broker.get_subscriber_count(GlueCellTopics.cell_state(cell_id)) == 1


def test_connect_subscribes_cell_glue_type_topics(clean_broker, adapter):
    for cell_id in [1, 2, 3]:
        assert clean_broker.get_subscriber_count(GlueCellTopics.cell_glue_type(cell_id)) == 1


def test_disconnect_removes_all_subscriptions(clean_broker, adapter):
    adapter.disconnect()
    for cell_id in [1, 2, 3]:
        assert clean_broker.get_subscriber_count(GlueCellTopics.cell_weight(cell_id)) == 0
        assert clean_broker.get_subscriber_count(GlueCellTopics.cell_state(cell_id)) == 0
        assert clean_broker.get_subscriber_count(GlueCellTopics.cell_glue_type(cell_id)) == 0


# ------------------------------------------------------------------ #
#  Message routing — weight / state / glue type                       #
# ------------------------------------------------------------------ #

def test_weight_published_calls_set_cell_weight(clean_broker, adapter, mock_ui):
    clean_broker.publish(GlueCellTopics.cell_weight(1), 2500.0)
    mock_ui.set_cell_weight.assert_called_once_with(1, 2500.0)


def test_state_dict_published_extracts_current_state(clean_broker, adapter, mock_ui):
    clean_broker.publish(GlueCellTopics.cell_state(2), {"current_state": "ready"})
    mock_ui.set_cell_state.assert_called_once_with(2, "ready")


def test_state_string_published_directly(clean_broker, adapter, mock_ui):
    clean_broker.publish(GlueCellTopics.cell_state(3), "error")
    mock_ui.set_cell_state.assert_called_once_with(3, "error")


def test_glue_type_published_calls_set_cell_glue_type(clean_broker, adapter, mock_ui):
    clean_broker.publish(GlueCellTopics.cell_glue_type(1), "PUR Hotmelt")
    mock_ui.set_cell_glue_type.assert_called_once_with(1, "PUR Hotmelt")


# ------------------------------------------------------------------ #
#  Application state → button configuration                           #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("state,exp_start,exp_stop,exp_pause", [
    (ApplicationState.IDLE,         True,  False, False),
    (ApplicationState.STARTED,      False, True,  True),
    (ApplicationState.PAUSED,       False, True,  True),
    (ApplicationState.ERROR,        False, True,  False),
    (ApplicationState.INITIALIZING, False, False, False),
    (ApplicationState.STOPPED,      False, False, False),
])
def test_app_state_configures_buttons(clean_broker, adapter, mock_ui,
                                      state, exp_start, exp_stop, exp_pause):
    clean_broker.publish(SystemTopics.APPLICATION_STATE, state.value)
    mock_ui.set_start_enabled.assert_called_with(exp_start)
    mock_ui.set_stop_enabled.assert_called_with(exp_stop)
    mock_ui.set_pause_enabled.assert_called_with(exp_pause)


def test_paused_state_sets_resume_pause_text(clean_broker, adapter, mock_ui):
    clean_broker.publish(SystemTopics.APPLICATION_STATE, ApplicationState.PAUSED.value)
    args, _ = mock_ui.set_pause_text.call_args
    assert "Resume" in args[0]


# ------------------------------------------------------------------ #
#  Localization                                                        #
# ------------------------------------------------------------------ #

def test_retranslate_calls_set_action_button_text_for_each_button(adapter, mock_ui):
    mock_ui.reset_mock()
    adapter.retranslateUi()
    # One call per ACTION_BUTTON (reset_errors, mode_toggle, clean) at minimum
    assert mock_ui.set_action_button_text.call_count >= len(GlueAdapter.ACTION_BUTTONS)


# ------------------------------------------------------------------ #
#  build_cards class method                                            #
# ------------------------------------------------------------------ #

def test_build_cards_returns_one_tuple_per_card():
    container = MagicMock()
    container.get_cell_capacity.return_value = 5000.0
    cards = GlueAdapter.build_cards(container)
    assert len(cards) == len(GlueAdapter.CARDS)


def test_build_cards_tuples_have_four_elements():
    container = MagicMock()
    container.get_cell_capacity.return_value = 5000.0
    for item in GlueAdapter.build_cards(container):
        widget, card_id, row, col = item   # must unpack without error
        assert isinstance(card_id, int)
