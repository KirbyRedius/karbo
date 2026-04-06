"""Async HTTP client for the Karbo Bot API."""

from __future__ import annotations

from typing import Optional

import aiohttp

from .errors import (
    APIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import Author, BotInfo, Member, Message, SentMessage, User

_DEFAULT_BASE_URL = "https://api.karboai.com"


class KarboBot:
    """Karbo Bot API client.

    Parameters
    ----------
    token:
        The bot token (``BOT_TOKEN``).
    base_url:
        API base URL. Defaults to ``https://api.karboai.com``.
    session:
        An existing ``aiohttp.ClientSession`` to reuse.
        If not provided, a new session is created on first request.
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._owns_session = session is None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Bot-Token": self._token},
            )
            self._owns_session = True
        return self._session

    async def close(self) -> None:
        """Close the underlying HTTP session (if we own it)."""
        if self._session and not self._session.closed and self._owns_session:
            await self._session.close()

    async def __aenter__(self) -> KarboBot:
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    # ── internal ─────────────────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        session = await self._get_session()
        url = f"{self._base_url}{path}"

        async with session.request(method, url, json=json, params=params) as resp:
            if resp.status == 401:
                raise AuthenticationError(await resp.text())
            if resp.status == 403:
                raise ForbiddenError(await resp.text())
            if resp.status == 404:
                raise NotFoundError(await resp.text())
            if resp.status == 400:
                raise ValidationError(await resp.text())
            if resp.status == 429:
                retry = resp.headers.get("Retry-After")
                raise RateLimitError(float(retry) if retry else None)
            if resp.status >= 400:
                raise APIError(resp.status, await resp.text())
            return await resp.json()

    # ── Bot info ─────────────────────────────────────────────────────────

    async def get_me(self) -> BotInfo:
        """Get information about the authenticated bot."""
        data = await self._request("GET", "/bot/me")
        return BotInfo(
            bot_id=data["bot_id"],
            name=data["name"],
            status=data["status"],
        )

    # ── Messages ─────────────────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        content: str = "",
        *,
        reply_to: Optional[str] = None,
        images: Optional[list[str]] = None,
    ) -> SentMessage:
        """Send a message to a chat.

        Parameters
        ----------
        chat_id:
            The chat to send the message to.
        content:
            Message text (up to 5000 characters). Can be empty if images are provided.
        reply_to:
            Optional ``message_id`` to reply to.
        images:
            Optional list of image URLs (from :meth:`upload_image`).
        """
        payload: dict = {"chat_id": chat_id, "content": content}
        if reply_to is not None:
            payload["reply_message_id"] = reply_to
        if images:
            payload["images"] = images
        data = await self._request("POST", "/bot/send-message", json=payload)
        return SentMessage(
            message_id=data["message_id"],
            created_time=data["created_time"],
        )

    async def upload_image(self, file_path: str) -> str:
        """Upload an image file and return its URL.

        Parameters
        ----------
        file_path:
            Local path to the image file (.jpg, .png, .webp, .gif).

        Returns
        -------
        str
            The public URL of the uploaded image. Pass this to
            :meth:`send_message` via the ``images`` parameter.
        """
        session = await self._get_session()
        url = f"{self._base_url}/bot/upload/image"
        filename = file_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]

        with open(file_path, "rb") as fh:
            form = aiohttp.FormData()
            form.add_field("file", fh, filename=filename)

            async with session.post(url, data=form) as resp:
                if resp.status == 401:
                    raise AuthenticationError(await resp.text())
                if resp.status == 403:
                    raise ForbiddenError(await resp.text())
                if resp.status == 413:
                    raise ValidationError("File too large (max 20 MB)")
                if resp.status >= 400:
                    raise APIError(resp.status, await resp.text())
                data = await resp.json()
                return data["url"]

    async def get_message(self, chat_id: str, message_id: str) -> Message:
        """Get a specific message from a chat."""
        data = await self._request("GET", f"/bot/chat/{chat_id}/message/{message_id}")
        author = None
        if "author" in data:
            a = data["author"]
            author = Author(
                user_id=a["user_id"],
                nickname=a["nickname"],
                avatar=a.get("avatar", ""),
            )
        return Message(
            message_id=data["message_id"],
            chat_id=data["chat_id"],
            user_id=data["user_id"],
            content=data["content"],
            created_time=data["created_time"],
            type=data["type"],
            reply_message_id=data.get("reply_message_id"),
            author=author,
            audio=data.get("audio"),
            sticker=data.get("sticker"),
            images=data.get("images", []),
        )

    # ── Chat members ─────────────────────────────────────────────────────

    async def get_chat_members(
        self,
        chat_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Member]:
        """List members of a chat the bot is in."""
        data = await self._request(
            "GET",
            f"/bot/chat/{chat_id}/members",
            params={"limit": limit, "offset": offset},
        )
        return [
            Member(
                user_id=m["user_id"],
                nickname=m["nickname"],
                avatar=m["avatar"],
                role=m.get("role", 0),
            )
            for m in data["items"]
        ]

    # ── User profiles ────────────────────────────────────────────────────

    async def get_user(self, user_id: str) -> User:
        """Get a user's public profile."""
        data = await self._request("GET", f"/bot/user/{user_id}")
        return User(
            user_id=data["user_id"],
            nickname=data["nickname"],
            avatar=data["avatar"],
            short_info=data.get("short_info", ""),
            role=data.get("role", 0),
        )

    # ── Chat actions ─────────────────────────────────────────────────────

    async def leave_chat(self, chat_id: str) -> None:
        """Leave a chat."""
        await self._request("POST", f"/bot/leave-chat/{chat_id}")

    async def kick_user(self, chat_id: str, user_id: str) -> None:
        """Kick a user from a chat (requires helper role)."""
        await self._request(
            "POST",
            f"/bot/chat/{chat_id}/kick",
            json={"user_id": user_id},
        )
