"""WebSocket listener for real-time events from the Karbo Bot API."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Optional

import socketio

from .models import AvatarFrame, Author, Message, MessageReaction

logger = logging.getLogger("karbo.ws")

_DEFAULT_WS_URL = "https://api.karboai.com"

EventHandler = Callable[..., Awaitable[None]]


class KarboBotWS:
    """Real-time WebSocket client for receiving chat events.

    Parameters
    ----------
    token:
        The bot token.
    ws_url:
        WebSocket base URL. Defaults to ``https://api.karboai.com``.
    """

    def __init__(
        self,
        token: str,
        *,
        ws_url: str = _DEFAULT_WS_URL,
    ) -> None:
        self._token = token
        self._ws_url = ws_url.rstrip("/")

        self._sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=0,  # unlimited
            reconnection_delay=1,
            reconnection_delay_max=30,
            logger=False,
            engineio_logger=False,
        )

        self._on_message: Optional[Callable[[Message], Awaitable[None]]] = None
        self._on_connect: Optional[Callable[[], Awaitable[None]]] = None
        self._on_disconnect: Optional[Callable[[], Awaitable[None]]] = None
        self._on_raw: dict[str, list[EventHandler]] = {}

        self._setup_internal_handlers()

    def _setup_internal_handlers(self) -> None:
        @self._sio.event
        async def connect():
            logger.info("Connected to Karbo WebSocket")
            if self._on_connect:
                await self._on_connect()

        @self._sio.event
        async def disconnect():
            logger.info("Disconnected from Karbo WebSocket")
            if self._on_disconnect:
                await self._on_disconnect()

        @self._sio.on("new_message")
        async def on_new_message(data: dict):
            msg = _parse_message(data)
            if self._on_message:
                await self._on_message(msg)
            for handler in self._on_raw.get("new_message", []):
                await handler(data)

    # ── decorator API ────────────────────────────────────────────────────

    def on_message(
        self, func: Callable[[Message], Awaitable[None]],
    ) -> Callable[[Message], Awaitable[None]]:
        """Register a handler for incoming chat messages.

        Usage::

            @ws.on_message
            async def handle(message: karbo.Message):
                print(message.content)
        """
        self._on_message = func
        return func

    def on_connect(
        self, func: Callable[[], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """Register a handler called when WebSocket connects."""
        self._on_connect = func
        return func

    def on_disconnect(
        self, func: Callable[[], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """Register a handler called when WebSocket disconnects."""
        self._on_disconnect = func
        return func

    def on(self, event: str) -> Callable[[EventHandler], EventHandler]:
        """Register a raw event handler.

        Usage::

            @ws.on("custom_event")
            async def handle(data):
                ...
        """
        def decorator(func: EventHandler) -> EventHandler:
            self._on_raw.setdefault(event, []).append(func)

            @self._sio.on(event)
            async def _wrapper(data: Any) -> None:
                await func(data)

            return func
        return decorator

    # ── lifecycle ────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Connect to the Karbo WebSocket server."""
        await self._sio.connect(
            self._ws_url,
            socketio_path="/bot/ws",
            auth={"bot_token": self._token},
            transports=["websocket"],
        )

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        await self._sio.disconnect()

    async def wait(self) -> None:
        """Block until the connection is closed."""
        await self._sio.wait()

    async def run_forever(self) -> None:
        """Connect and block until disconnected. Convenience wrapper."""
        await self.connect()
        await self.wait()


def _parse_message(data: dict) -> Message:
    author = None
    if "author" in data and isinstance(data["author"], dict):
        a = data["author"]
        avatar_frame = None
        if isinstance(a.get("avatar_frame"), dict):
            avatar_frame = AvatarFrame(
                frame_id=a["avatar_frame"].get("frame_id"),
                file=a["avatar_frame"].get("file"),
            )
        author = Author(
            user_id=a.get("user_id", ""),
            nickname=a.get("nickname", "User"),
            avatar=a.get("avatar", a.get("avatar_url", "")),
            role=int(a.get("role", 0) or 0),
            app_role=int(a.get("app_role", 0) or 0),
            panel_color=a.get("panel_color"),
            level=int(a.get("level", 0) or 0),
            nickname_color=a.get("nickname_color"),
            nickname_emoji=a.get("nickname_emoji"),
            avatar_frame=avatar_frame,
        )
    reactions = [
        MessageReaction(
            reaction=item.get("reaction", ""),
            is_sticker=bool(item.get("is_sticker", False)),
            count=int(item.get("count", 0) or 0),
            me=bool(item.get("me", False)),
        )
        for item in data.get("reactions", [])
        if isinstance(item, dict)
    ]
    return Message(
        message_id=data.get("message_id", ""),
        chat_id=data.get("chat_id", ""),
        user_id=data.get("user_id", ""),
        content=data.get("content", ""),
        created_time=data.get("created_time", 0),
        type=data.get("type", 0),
        reply_message_id=data.get("reply_message_id"),
        author=author,
        audio=data.get("audio"),
        sticker=data.get("sticker"),
        images=data.get("images", []),
        bubble_id=data.get("bubble_id"),
        bubble_version=int(data.get("bubble_version", 0) or 0),
        reactions=reactions,
    )
