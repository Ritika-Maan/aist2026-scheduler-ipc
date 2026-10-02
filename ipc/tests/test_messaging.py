import pytest

from ipc.messaging import (
    AsyncMessageChannel,
    MessagePassingConfig,
    message_overhead,
)


def test_zero_latency_message_is_immediately_available():
    channel = AsyncMessageChannel(
        MessagePassingConfig(latency=0.0)
    )

    event = channel.send("A", "B", 10.0)

    assert event.available_time == pytest.approx(10.0)

    received = channel.receive("B", 10.0)

    assert received is not None
    assert received.sender == "A"
    assert received.receiver == "B"


def test_configured_latency_delays_message():
    channel = AsyncMessageChannel(
        MessagePassingConfig(latency=2.5)
    )

    event = channel.send("A", "B", 10.0)

    assert event.available_time == pytest.approx(12.5)

    assert channel.receive("B", 12.0) is None

    received = channel.receive("B", 12.5)

    assert received is not None
    assert received.latency == pytest.approx(2.5)


def test_message_passing_is_buffered():
    channel = AsyncMessageChannel(
        MessagePassingConfig(latency=1.0)
    )

    channel.send("A", "B", 0.0)
    channel.send("A", "B", 0.5)

    assert channel.pending() == 2
    assert channel.pending_for("B") == 2

    first = channel.receive("B", 1.0)

    assert first is not None
    assert first.send_time == pytest.approx(0.0)
    assert channel.pending() == 1


def test_message_for_other_receiver_is_not_consumed():
    channel = AsyncMessageChannel(
        MessagePassingConfig(latency=0.0)
    )

    channel.send("A", "B", 0.0)

    assert channel.receive("C", 0.0) is None
    assert channel.pending() == 1


def test_latency_is_configurable():
    fast = MessagePassingConfig(latency=0.5)
    slow = MessagePassingConfig(latency=2.0)

    assert message_overhead(fast) == pytest.approx(0.5)
    assert message_overhead(slow) == pytest.approx(2.0)


def test_negative_latency_rejected():
    with pytest.raises(ValueError):
        MessagePassingConfig(latency=-1.0)


def test_invalid_capacity_rejected():
    with pytest.raises(ValueError):
        MessagePassingConfig(latency=1.0, capacity=0)


def test_buffer_capacity():
    channel = AsyncMessageChannel(
        MessagePassingConfig(latency=1.0, capacity=1)
    )

    channel.send("A", "B", 0.0)

    with pytest.raises(BufferError):
        channel.send("A", "B", 0.1)