"""
Tests for MessageBroker — singleton, pub/sub, weak-reference cleanup.
No Qt required.
"""
import gc

import pytest

from external_dependencies.MessageBroker import MessageBroker


# ------------------------------------------------------------------ #
#  Singleton                                                           #
# ------------------------------------------------------------------ #

def test_singleton():
    assert MessageBroker() is MessageBroker()


# ------------------------------------------------------------------ #
#  Subscribe / Publish                                                 #
# ------------------------------------------------------------------ #

def test_subscribe_and_publish(clean_broker):
    received = []
    callback = lambda msg: received.append(msg)   # noqa: E731 — strong ref kept
    clean_broker.subscribe("test/topic", callback)
    clean_broker.publish("test/topic", "hello")
    assert received == ["hello"]


def test_publish_multiple_subscribers(clean_broker):
    results = []
    cb1 = lambda msg: results.append(("a", msg))  # noqa: E731
    cb2 = lambda msg: results.append(("b", msg))  # noqa: E731
    clean_broker.subscribe("t", cb1)
    clean_broker.subscribe("t", cb2)
    clean_broker.publish("t", 42)
    assert ("a", 42) in results
    assert ("b", 42) in results


def test_publish_unknown_topic_is_safe(clean_broker):
    clean_broker.publish("no/such/topic", "data")  # must not raise


def test_unsubscribe_stops_delivery(clean_broker):
    received = []
    callback = lambda msg: received.append(msg)  # noqa: E731
    clean_broker.subscribe("t", callback)
    clean_broker.unsubscribe("t", callback)
    clean_broker.publish("t", "hello")
    assert received == []


# ------------------------------------------------------------------ #
#  Weak-reference GC behaviour                                        #
# ------------------------------------------------------------------ #

def test_dead_bound_method_not_called(clean_broker):
    """Bound method weak-ref is collected when the object is deleted."""
    received = []

    class Receiver:
        def on_msg(self, msg):
            received.append(msg)

    r = Receiver()
    clean_broker.subscribe("t", r.on_msg)
    del r
    gc.collect()
    clean_broker.publish("t", "ping")
    assert received == []


# ------------------------------------------------------------------ #
#  Subscriber count                                                    #
# ------------------------------------------------------------------ #

def test_get_subscriber_count(clean_broker):
    cb = lambda _: None  # noqa: E731
    clean_broker.subscribe("t", cb)
    assert clean_broker.get_subscriber_count("t") == 1


def test_clear_all_removes_all_subscribers(clean_broker):
    cb = lambda _: None  # noqa: E731
    clean_broker.subscribe("a", cb)
    clean_broker.subscribe("b", cb)
    clean_broker.clear_all()
    assert clean_broker.get_subscriber_count("a") == 0
    assert clean_broker.get_subscriber_count("b") == 0
