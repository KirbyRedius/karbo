"""Async HTTP client for the Karbo Bot API."""

from __future__ import annotations

from typing import Any, Optional

import aiohttp

from .errors import (
    APIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .buttons import Button, Row, buttons_to_dict
from .models import (
    AvatarFrame,
    Author,
    BotInfo,
    Chat,
    LastMessagePreview,
    Member,
    Message,
    MessageReaction,
    SentMessage,
    User,
)

_DEFAULT_BASE_URL = "https://api.karboai.com"


def _opt_int(val: Any) -> int | None:
    if val is None:
        return None
    return int(val)


def _parse_avatar_frame(data: dict | None) -> AvatarFrame | None:
    if not isinstance(data, dict):
        return None
    return AvatarFrame(
        frame_id=data.get("frame_id"),
        file=data.get("file"),
    )


def _parse_author(data: dict | None) -> Author | None:
    if not isinstance(data, dict):
        return None
    return Author(
        user_id=data.get("user_id", ""),
        nickname=data.get("nickname", "User"),
        avatar=data.get("avatar", data.get("avatar_url", "")) or "",
        role=int(data.get("role", 0) or 0),
        app_role=int(data.get("app_role", 0) or 0),
        panel_color=data.get("panel_color"),
        level=int(data.get("level", 0) or 0),
        nickname_color=data.get("nickname_color"),
        nickname_emoji=data.get("nickname_emoji"),
        avatar_frame=_parse_avatar_frame(data.get("avatar_frame")),
        is_api_bot=bool(data.get("is_api_bot", False)),
    )


def _parse_last_message_preview(data: dict | None) -> LastMessagePreview | None:
    if not isinstance(data, dict):
        return None
    author = data.get("author") if isinstance(data.get("author"), dict) else {}
    return LastMessagePreview(
        message_id=data.get("message_id", "") or "",
        created_time=int(data.get("created_time", 0) or 0),
        content=data.get("content", "") or "",
        type=int(data.get("type", 0) or 0),
        user_id=data.get("user_id", "") or "",
        has_images=bool(data.get("has_images", False)),
        audio=data.get("audio"),
        sticker=data.get("sticker"),
        video_note=data.get("video_note"),
        author_nickname=(author or {}).get("nickname", "") or "",
        author_avatar=(author or {}).get("avatar_url", (author or {}).get("avatar", "")) or "",
    )


def _parse_reactions(items: list[dict] | None) -> list[MessageReaction]:
    if not items:
        return []
    return [
        MessageReaction(
            reaction=item.get("reaction", ""),
            is_sticker=bool(item.get("is_sticker", False)),
            count=int(item.get("count", 0) or 0),
            me=bool(item.get("me", False)),
        )
        for item in items
        if isinstance(item, dict)
    ]


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
        buttons: Optional[list[Row]] = None,
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
        buttons:
            Optional list of rows of inline buttons. Each row is a list
            of :class:`karbo.Button` objects (or raw ``dict``s for
            advanced use). A single :class:`karbo.Button` instead of a
            list is treated as a one-button row. See ``karbo/buttons.py``
            for available styles, animations, and particle effects.
        """
        payload: dict = {"chat_id": chat_id, "content": content}
        if reply_to is not None:
            payload["reply_message_id"] = reply_to
        if images:
            payload["images"] = images
        if buttons:
            payload["inline_buttons"] = buttons_to_dict(buttons)
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
        author = _parse_author(data.get("author"))
        chat_type_raw = data.get("chat_type")
        return Message(
            message_id=data["message_id"],
            chat_id=data["chat_id"],
            user_id=data["user_id"],
            content=data["content"],
            created_time=data["created_time"],
            type=data["type"],
            community_id=int(data.get("community_id", 0) or 0),
            chat_type=int(chat_type_raw) if chat_type_raw is not None else None,
            reply_message_id=data.get("reply_message_id"),
            author=author,
            audio=data.get("audio"),
            audio_duration_ms=_opt_int(data.get("audio_duration_ms")),
            waveform=data.get("waveform"),
            video_note=data.get("video_note"),
            video_note_duration_ms=_opt_int(data.get("video_note_duration_ms")),
            sticker=data.get("sticker"),
            images=data.get("images", []),
            transparent=bool(data.get("transparent", False)),
            bubble_id=data.get("bubble_id"),
            bubble_version=int(data.get("bubble_version", 0) or 0),
            reactions=_parse_reactions(data.get("reactions")),
        )

    async def get_chat(self, chat_id: str) -> Chat:
        """Get full metadata for a chat the bot is in.

        Returns the same payload shape as the app-facing
        ``GET /chat/{chat_id}`` endpoint: chat kind (``type`` — see
        ``CHAT_TYPE_*`` constants), title, community, pinned message,
        member count, last-message preview, and (for DMs) the other
        party's profile snapshot. Fields the SDK doesn't project onto
        typed attributes are preserved in ``Chat.raw``.

        Raises ``ForbiddenError`` if the bot is not a member of the
        requested chat.
        """
        data = await self._request("GET", f"/bot/chat/{chat_id}")
        last = _parse_last_message_preview(data.get("last_message"))
        return Chat(
            chat_id=data.get("chat_id", chat_id),
            type=int(data.get("type", 0) or 0),
            title=data.get("title", "") or "",
            community_id=int(data.get("community_id", 0) or 0),
            chatting_type=int(data.get("chatting_type", 0) or 0),
            background=data.get("background"),
            icon=data.get("icon"),
            chat_description=data.get("chat_description", "") or "",
            pinned_message=data.get("pinned_message", "") or "",
            everyone_can_invite=bool(data.get("everyone_can_invite", True)),
            voice_invite_only=bool(data.get("voice_invite_only", False)),
            is_voice_active=bool(data.get("is_voice_active", False)),
            is_cinema_active=bool(data.get("is_cinema_active", False)),
            is_hidden=int(data.get("is_hidden", 0) or 0),
            created_time=int(data.get("created_time", 0) or 0),
            creator_user_id=data.get("creator_user_id", "") or "",
            creator_nickname=data.get("creator_nickname", "") or "",
            creator_avatar_url=data.get("creator_avatar_url", "") or "",
            users_count=int(data.get("users_count", 0) or 0),
            is_chat_member=bool(data.get("is_chat_member", True)),
            member_status=data.get("member_status", "joined") or "joined",
            is_muted_chat=bool(data.get("is_muted_chat", False)),
            last_readed_message_id=data.get("last_readed_message_id"),
            helper_ids=list(data.get("helper_ids") or []),
            other_user_id=data.get("other_user_id", "") or "",
            other_user_nickname=data.get("other_user_nickname", "") or "",
            other_user_avatar_url=data.get("other_user_avatar_url", "") or "",
            last_message=last,
            raw=dict(data),
        )

    # ── Chat members ─────────────────────────────────────────────────────

    async def get_chat_members(
        self,
        chat_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        community_id: Optional[int] = None,
    ) -> list[Member]:
        """List members of a chat the bot is in.

        Parameters
        ----------
        community_id:
            Optional community ID. When provided, member profiles
            (nickname, avatar, role, level) are resolved from that
            community instead of the global profile.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if community_id is not None:
            params["community_id"] = community_id
        data = await self._request(
            "GET",
            f"/bot/chat/{chat_id}/members",
            params=params,
        )
        return [
            Member(
                user_id=m["user_id"],
                nickname=m["nickname"],
                avatar=m.get("avatar", m.get("avatar_url", "")),
                role=m.get("role", 0),
                app_role=m.get("app_role", 0),
                panel_color=m.get("panel_color"),
                level=m.get("level", 0),
                nickname_color=m.get("nickname_color"),
                nickname_emoji=m.get("nickname_emoji"),
                avatar_frame=_parse_avatar_frame(m.get("avatar_frame")),
                member_status=m.get("member_status", "joined"),
                is_api_bot=bool(m.get("is_api_bot", False)),
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
            avatar=data.get("avatar", data.get("avatar_url", "")),
            short_info=data.get("short_info", ""),
            role=data.get("role", 0),
            app_role=data.get("app_role", 0),
            panel_color=data.get("panel_color"),
            level=data.get("level", 0),
            nickname_color=data.get("nickname_color"),
            nickname_emoji=data.get("nickname_emoji"),
            avatar_frame=_parse_avatar_frame(data.get("avatar_frame")),
            bubble_id=data.get("bubble_id"),
        )

    async def get_user_in_community(self, user_id: str, community_id: int) -> User:
        """Get a user's profile within a specific community."""
        data = await self._request("GET", f"/bot/user/{user_id}/community/{community_id}")
        return User(
            user_id=data["user_id"],
            nickname=data["nickname"],
            avatar=data.get("avatar", data.get("avatar_url", "")),
            short_info=data.get("short_info", ""),
            role=data.get("role", 0),
            app_role=data.get("app_role", 0),
            panel_color=data.get("panel_color"),
            level=data.get("level", 0),
            nickname_color=data.get("nickname_color"),
            nickname_emoji=data.get("nickname_emoji"),
            avatar_frame=_parse_avatar_frame(data.get("avatar_frame")),
            bubble_id=data.get("bubble_id"),
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
