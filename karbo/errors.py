"""Exception hierarchy for the Karbo SDK."""

from __future__ import annotations


class KarboError(Exception):
    """Base exception for all Karbo SDK errors."""


class AuthenticationError(KarboError):
    """Invalid or missing bot token."""


class ForbiddenError(KarboError):
    """The bot does not have permission to perform this action."""


class NotFoundError(KarboError):
    """The requested resource was not found."""


class ValidationError(KarboError):
    """The request payload is invalid."""


class RateLimitError(KarboError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: float | None = None):
        self.retry_after = retry_after
        msg = "Rate limit exceeded"
        if retry_after is not None:
            msg += f" (retry after {retry_after}s)"
        super().__init__(msg)


class APIError(KarboError):
    """Unexpected API error."""

    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")
