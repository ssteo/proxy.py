# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
from typing import Optional, Any

from ..http.parser import HttpParser, httpParserTypes, httpParserStates
from ..http.proxy import HttpProxyBasePlugin


class ModifyChunkResponsePlugin(HttpProxyBasePlugin):
    """Accumulate & modify chunk responses as received from upstream."""

    DEFAULT_CHUNKS = [
        b'modify',
        b'chunk',
        b'response',
        b'plugin',
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Create a new http protocol parser for response payloads
        self.response = HttpParser(httpParserTypes.RESPONSE_PARSER)

    def before_upstream_connection(
            self, request: HttpParser) -> Optional[HttpParser]:
        return request

    def handle_client_request(
            self, request: HttpParser) -> Optional[HttpParser]:
        return request

    def handle_upstream_chunk(self, chunk: memoryview) -> memoryview:
        # Parse the response.
        # Note that these chunks also include headers
        self.response.parse(chunk.tobytes())
        # If response is complete, modify and dispatch to client
        if self.response.state == httpParserStates.COMPLETE:
            self.response.body = b'\n'.join(self.DEFAULT_CHUNKS) + b'\n'
            self.client.queue(memoryview(self.response.build_response()))
        return memoryview(b'')

    def on_upstream_connection_close(self) -> None:
        pass
