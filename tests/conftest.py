import sys
from pathlib import Path

# Ensure src/ is on the path so both `external_dependencies.*` and
# `glue_dispensing_dashboard.*` resolve to the same module objects that
# run_app.py uses.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from external_dependencies.MessageBroker import MessageBroker


@pytest.fixture(autouse=True)
def clean_broker():
    """Reset the MessageBroker singleton before and after every test.

    MessageBroker is a process-wide singleton; without this fixture
    subscriptions from one test would leak into the next.
    """
    broker = MessageBroker()
    broker.clear_all()
    yield broker
    broker.clear_all()