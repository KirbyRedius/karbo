"""Data models returned by the Karbo Bot API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ── Chat type constants ─────────────────────────────────────────────────
# Server-side ChatType enum values (see backend `constants.py`). Exposed
# as module-level ints so bot code can branch on the field without
# importing enum values via magic numbers.
#
# CHAT_TYPE_PUBLIC   public group chat (community-owned)
# CHAT_TYPE_BOT      legacy "bot-DM" flag — kept for compatibility, most
#                    bot DMs use CHAT_TYPE_PM instead
# CHAT_TYPE_PM       private message (user-user OR user-bot DM)
# CHAT_TYPE_PRIVATE  private group chat (invite-only)
CHAT_TYPE_PUBLIC = 0
CHAT_TYPE_BOT = 1
CHAT_TYPE_PM = 2
CHAT_TYPE_PRIVATE = 3


# ── Message type constants ──────────────────────────────────────────────
# The most frequently-checked values from the server's `MessageType` enum.
# See docs.karboai.com for the full table. Bot code typically only cares
# about NORMAL_MESSAGE, CREATE_CHAT_MESSAGE (DM opened with the bot), and
# INVITED_BOT_TO_CHAT (bot added to a chat).
NORMAL_MESSAGE = 0
JOIN_CHAT_MESSAGE = 1
LEAVE_CHAT_MESSAGE = 2
KICK_CHAT_MESSAGE = 3
CREATE_CHAT_MESSAGE = 4        # DM opened with the bot (first time)
USER_DELETED_MESSAGE = 5
ADMIN_DELETED_MESSAGE = 6
VOICE_CHAT_STARTED = 7
VOICE_CHAT_ENDED = 8
BACKGROUND_CHANGED = 9
INVITED_USER_TO_CHAT = 10
INVITED_BOT_TO_CHAT = 11       # this bot was added to a chat


@dataclass(frozen=True, slots=True)
class BotInfo:
    """Information about the authenticated bot (/bot/me)."""

    bot_id: str
    name: str
    status: str  # "not_official" | "official" | "banned"


@dataclass(frozen=True, slots=True)
class AvatarFrame:
    """Selected avatar frame."""

    frame_id: Optional[str] = None
    file: Optional[str] = None


@dataclass(frozen=True, slots=True)
class MessageReaction:
    """Aggregated reaction entry for a message."""

    reaction: str
    is_sticker: bool = False
    count: int = 0
    me: bool = False


@dataclass(frozen=True, slots=True)
class User:
    """Public user profile."""

    user_id: str
    nickname: str
    avatar: str
    short_info: str = ""
    role: int = 0
    app_role: int = 0
    panel_color: Optional[str] = None
    level: int = 0
    nickname_color: Optional[str] = None
    nickname_emoji: Optional[str] = None
    avatar_frame: Optional[AvatarFrame] = None
    bubble_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class Member:
    """Chat member entry."""

    user_id: str
    nickname: str
    avatar: str
    role: int = 0
    app_role: int = 0
    panel_color: Optional[str] = None
    level: int = 0
    nickname_color: Optional[str] = None
    nickname_emoji: Optional[str] = None
    avatar_frame: Optional[AvatarFrame] = None
    member_status: str = "joined"
    is_api_bot: bool = False


@dataclass(frozen=True, slots=True)
class Author:
    """Message author info embedded in a message."""

    user_id: str
    nickname: str
    avatar: str = ""
    role: int = 0
    app_role: int = 0
    panel_color: Optional[str] = None
    level: int = 0
    nickname_color: Optional[str] = None
    nickname_emoji: Optional[str] = None
    avatar_frame: Optional[AvatarFrame] = None
    is_api_bot: bool = False


@dataclass(frozen=True, slots=True)
class Message:
    """A single chat message.

    Attributes
    ----------
    type:
        Message type (see module-level ``NORMAL_MESSAGE``,
        ``CREATE_CHAT_MESSAGE``, ``INVITED_BOT_TO_CHAT`` constants and
        docs.karboai.com for the full table).
    chat_type:
        Kind of the containing chat (``CHAT_TYPE_PUBLIC``,
        ``CHAT_TYPE_PM``, ``CHAT_TYPE_PRIVATE``, ``CHAT_TYPE_BOT``).
        Present on all WebSocket events; may be ``None`` on REST
        responses that pre-date the field.
    community_id:
        Community the chat lives in (``0`` for DMs and global chats).
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
    community_id: int = 0
    chat_type: Optional[int] = None
    reply_message_id: Optional[str] = None
    author: Optional[Author] = None
    audio: Optional[str] = None
    audio_duration_ms: Optional[int] = None
    waveform: Optional[list[float]] = None
    video_note: Optional[str] = None
    video_note_duration_ms: Optional[int] = None
    sticker: Optional[str] = None
    images: list[str] = field(default_factory=list)
    transparent: bool = False
    bubble_id: Optional[str] = None
    bubble_version: int = 0
    reactions: list[MessageReaction] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SentMessage:
    """Result of sending a message."""

    message_id: str
    created_time: int


@dataclass(frozen=True, slots=True)
class LastMessagePreview:
    """Compact snapshot of the last message in a chat, as returned by
    ``KarboBot.get_chat()``. Not a full :class:`Message`.
    """

    message_id: str
    created_time: int
    content: str
    type: int
    user_id: str
    has_images: bool = False
    audio: Optional[str] = None
    sticker: Optional[str] = None
    video_note: Optional[str] = None
    author_nickname: str = ""
    author_avatar: str = ""


@dataclass(frozen=True, slots=True)
class Chat:
    """Full chat metadata, as returned by ``KarboBot.get_chat()``.

    ``type`` uses the module-level ``CHAT_TYPE_*`` constants
    (``CHAT_TYPE_PUBLIC``, ``CHAT_TYPE_BOT``, ``CHAT_TYPE_PM``,
    ``CHAT_TYPE_PRIVATE``). ``community_id`` is ``0`` for DMs and
    global chats.

    For DMs, ``other_user_id`` / ``other_user_nickname`` /
    ``other_user_avatar_url`` describe the human on the other side of
    the DM (empty strings for group chats).

    ``last_message`` is ``None`` if the chat has no messages yet.

    ``raw`` preserves the full server payload (same shape as the user
    app's ``GET /chat/{chat_id}``) — useful for fields we haven't
    projected onto the dataclass yet, without waiting for an SDK release.
    """

    chat_id: str
    type: int
    title: str = ""
    community_id: int = 0
    chatting_type: int = 0
    background: Optional[str] = None
    icon: Optional[str] = None
    chat_description: str = ""
    pinned_message: str = ""
    everyone_can_invite: bool = True
    voice_invite_only: bool = False
    is_voice_active: bool = False
    is_cinema_active: bool = False
    is_hidden: int = 0
    created_time: int = 0
    creator_user_id: str = ""
    creator_nickname: str = ""
    creator_avatar_url: str = ""
    users_count: int = 0
    is_chat_member: bool = True
    member_status: str = "joined"
    is_muted_chat: bool = False
    last_readed_message_id: Optional[str] = None
    helper_ids: list[str] = field(default_factory=list)
    other_user_id: str = ""
    other_user_nickname: str = ""
    other_user_avatar_url: str = ""
    last_message: Optional[LastMessagePreview] = None
    raw: dict[str, Any] = field(default_factory=dict)
