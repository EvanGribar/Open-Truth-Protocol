from __future__ import annotations


class OTPError(Exception):
    """Base error for OTP services."""


class ConfigError(OTPError):
    """Raised when required runtime configuration is invalid."""


class ValidationError(OTPError):
    """Raised when payload validation fails."""


class RetryableProcessingError(OTPError):
    """Raised for transient processing failures."""


class NonRetryableProcessingError(OTPError):
    """Raised for terminal processing failures."""
