"""Karbo — Official Python SDK for KarboAI Bot API."""

from .buttons import (
    Button,
    ButtonPress,
    ButtonStyle,
    ConfettiParticles,
    Glitch,
    Gradient,
    HeartParticles,
    Neon,
    Outline,
    Particles,
    PixelParticles,
    Pulse,
    SmokeParticles,
    SparkParticles,
    SwipeInteraction,
    TapInteraction,
    buttons_to_dict,
)
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
from .models import (
    AvatarFrame,
    Author,
    BotInfo,
    Member,
    Message,
    MessageReaction,
    SentMessage,
    User,
)
from .ws import KarboBotWS

__all__ = [
    "KarboBot",
    "KarboBotWS",
    # Models
    "AvatarFrame",
    "Author",
    "BotInfo",
    "Member",
    "Message",
    "MessageReaction",
    "SentMessage",
    "User",
    # Buttons API
    "Button",
    "ButtonPress",
    "ButtonStyle",
    "Gradient",
    "TapInteraction",
    "SwipeInteraction",
    "Pulse",
    "Neon",
    "Glitch",
    "Outline",
    "Particles",
    "SparkParticles",
    "ConfettiParticles",
    "HeartParticles",
    "PixelParticles",
    "SmokeParticles",
    "buttons_to_dict",
    # Errors
    "KarboError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]

__version__ = "0.8.1"
