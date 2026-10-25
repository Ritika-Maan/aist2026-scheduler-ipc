"""
Asynchronous/buffered message-passing model for the IPC experiments.

The baseline message-passing model does not use mutex-style blocking.
A sender enqueues a message and the receiver can consume it after the
configured communication latency.

Latency is configurable so the experiment harness can later sweep it.
"""

from dataclasses import dataclass
from collections import deque
from typing import Any


@dataclass(frozen=True)
class MessagePassingConfig:
    """Configuration for asynchronous message passing."""

    latency: float = 0.0
    capacity: int | None = None

    def __post_init__(self):
        if self.latency < 0:
            raise ValueError("message latency must be non-negative")

        if self.capacity is not None and self.capacity <= 0:
            raise ValueError("message capacity must be positive")


@dataclass(frozen=True)
class Message:
    """A buffered message."""

    sender: str
    receiver: str
    send_time: float
    payload: Any = None

    @property
    def key(self):
        return (self.sender, self.receiver, self.send_time)


@dataclass(frozen=True)
class MessageEvent:
    """Record of a message transmission."""

    sender: str
    receiver: str
    send_time: float
    available_time: float
    latency: float


class AsyncMessageChannel:
    """
    Buffered asynchronous message channel.

    Sending never blocks on receiver execution in the baseline model.
    A message becomes available after `config.latency`.
    """

    def __init__(self, config: MessagePassingConfig | None = None):
        self.config = config or MessagePassingConfig()
        self._queue: deque[MessageEvent] = deque()
        self.events: list[MessageEvent] = []

    def send(
        self,
        sender: str,
        receiver: str,
        send_time: float,
        payload: Any = None,
    ) -> MessageEvent:
        """Send a buffered message and record its communication latency."""

        event = MessageEvent(
            sender=sender,
            receiver=receiver,
            send_time=float(send_time),
            available_time=float(send_time) + self.config.latency,
            latency=self.config.latency,
        )

        if (
            self.config.capacity is not None
            and len(self._queue) >= self.config.capacity
        ):
            raise BufferError("message buffer is full")

        self._queue.append(event)
        self.events.append(event)

        return event

    def receive(
        self,
        receiver: str,
        current_time: float,
    ) -> MessageEvent | None:
        """
        Return the earliest available message for `receiver`.

        Returns None if no message is currently available.
        """

        for event in self._queue:
            if (
                event.receiver == receiver
                and event.available_time <= current_time + 1e-9
            ):
                self._queue.remove(event)
                return event

        return None

    def pending(self) -> int:
        """Return the number of buffered messages."""

        return len(self._queue)

    def pending_for(self, receiver: str) -> int:
        """Return the number of buffered messages for a receiver."""

        return sum(
            event.receiver == receiver
            for event in self._queue
        )

    def clear(self) -> None:
        """Clear pending messages and recorded events."""

        self._queue.clear()
        self.events.clear()


def message_overhead(
    config: MessagePassingConfig | None = None,
) -> float:
    """Return the configured communication latency."""

    return (config or MessagePassingConfig()).latency
