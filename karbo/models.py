"""Data models returned by the Karbo Bot API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True, slots=True)
class BotInfo:
    """Information about the authenticated bot (/bot/me)."""

    bot_id: str
    name: str
    status: str  # "not_official" | "official" | "banned"


@dataclass(frozen=True, slots=True)
class User:
    """Public user profile."""

    user_id: str
    nickname: str
    avatar: str
    short_info: str = ""
    role: int = 0


@dataclass(frozen=True, slots=True)
class Member:
    """Chat member entry."""

    user_id: str
    nickname: str
    avatar: str
    role: int = 0


@dataclass(frozen=True, slots=True)
class Author:
    """Message author info embedded in a message."""

    user_id: str
    nickname: str
    avatar: str = ""


@dataclass(frozen=True, slots=True)
class Message:
    """A single chat message.

    Attributes
    ----------
    type:
        0 = normal text, other values = system messages.
    audio:
        URL of a voice message, if present.
    sticker:
        Sticker identifier or URL, if present.
    images:
        List of image URLs attached to the message.
    """

    message_id: str
    chat_id: str
    user_id: str
    content: str
    created_time: int
    type: int
    reply_message_id: Optional[str] = None
    author: Optional[Author] = None
    audio: Optional[str] = None
    sticker: Optional[str] = None
    images: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SentMessage:
    """Result of sending a message."""

    message_id: str
    created_time: int
