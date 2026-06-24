"""Karbo — Official Python SDK for KarboAI Bot API."""

from .client import KarboBot
from .errors import (
    APIError,
    AuthenticationError,
    ForbiddenError,
    KarboError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import AvatarFrame, Author, BotInfo, Member, Message, MessageReaction, SentMessage, User
from .ws import KarboBotWS

__all__ = [
    "KarboBot",
    "KarboBotWS",
    "AvatarFrame",
    "Author",
    "BotInfo",
    "Member",
    "Message",
    "MessageReaction",
    "SentMessage",
    "User",
    "KarboError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]

__version__ = "0.4.0"
