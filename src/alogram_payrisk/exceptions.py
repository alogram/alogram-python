# Copyright (c) 2025 Alogram Inc.
# All rights reserved.


from typing import Optional


class AlogramError(Exception):
    """Base exception for all Alogram SDK errors."""

    def __init__(self, message: str, status: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status = status
        self.body = body


class AuthenticationError(AlogramError):
    """Raised when API Key or JWT validation fails."""

    pass


class RateLimitError(AlogramError):
    """Raised when the client is being throttled (HTTP 429)."""

    pass


class ValidationError(AlogramError):
    """Raised when the request payload does not match the schema."""

    pass


class InternalServerError(AlogramError):
    """Raised when the Alogram platform encounters an internal error (HTTP 5xx)."""

    pass


class ScopedAccessError(AlogramError):
    """Raised when an SDK method is called using a key that does not have the required trust scope."""

    def __init__(self, message: str):
        super().__init__(message, status=403)
