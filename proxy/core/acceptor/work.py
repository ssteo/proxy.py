# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import argparse
import socket

from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from typing import Optional, Dict, Any

from ..event import eventNames, EventQueue
from ..connection import TcpClientConnection
from ...common.types import Readables, Writables


class Work(ABC):
    """Implement Work to hook into the event loop provided by Threadless process."""

    def __init__(
            self,
            client: TcpClientConnection,
            flags: argparse.Namespace,
            event_queue: Optional[EventQueue] = None,
            uid: Optional[UUID] = None) -> None:
        self.client = client
        self.flags = flags
        self.event_queue = event_queue
        self.uid: UUID = uid if uid is not None else uuid4()

    @abstractmethod
    def get_events(self) -> Dict[socket.socket, int]:
        """Return sockets and events (read or write) that we are interested in."""
        return {}   # pragma: no cover

    @abstractmethod
    def handle_events(
            self,
            readables: Readables,
            writables: Writables) -> bool:
        """Handle readable and writable sockets.

        Return True to shutdown work."""
        return False    # pragma: no cover

    def initialize(self) -> None:
        """Perform any resource initialization."""
        pass    # pragma: no cover

    def is_inactive(self) -> bool:
        """Return True if connection should be considered inactive."""
        return False    # pragma: no cover

    def shutdown(self) -> None:
        """Implementation must close any opened resources here
        and call super().shutdown()."""
        self.publish_event(
            event_name=eventNames.WORK_FINISHED,
            event_payload={},
            publisher_id=self.__class__.__name__
        )

    def run(self) -> None:
        """run() method is not used by Threadless.  It's here for backward
        compatibility with threaded mode where work class is started as
        a separate thread.
        """
        pass

    def publish_event(
            self,
            event_name: int,
            event_payload: Dict[str, Any],
            publisher_id: Optional[str] = None) -> None:
        """Convenience method provided to publish events into the global event queue."""
        if not self.flags.enable_events:
            return
        assert self.event_queue
        self.event_queue.publish(
            self.uid.hex,
            event_name,
            event_payload,
            publisher_id
        )
