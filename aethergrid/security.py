"""
security.py
===========
Credential hashing and verification for AetherGrid.

Provides salted SHA-256 password hashing, constant-time credential
verification, and safe loading of a credentials file. Every failure
raises :class:`AuthenticationError` so callers never see raw
``FileNotFoundError``, ``PermissionError``, or ``ValueError``.
"""

import base64
import hashlib
import hmac
import os
from typing import Dict

from aethergrid.exceptions import AuthenticationError


SALT_BYTES = 16
HASH_NAME = "sha256"
SEPARATOR = "$"


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Return a salted SHA-256 hash string for a plaintext password.

    Parameters
    ----------
    password : str
        Non-empty plaintext password.

    Returns
    -------
    str
        A string of the form ``salt$digest``. The salt is base64-encoded
        random bytes; the digest is the hex-encoded SHA-256 hash of the
        salt concatenated with the password.

    Raises
    ------
    AuthenticationError
        If ``password`` is not a non-empty string.
    """
    if not isinstance(password, str) or not password:
        raise AuthenticationError("password must be a non-empty string")

    salt_bytes = os.urandom(SALT_BYTES)
    salt_b64 = base64.b64encode(salt_bytes).decode("utf-8")

    combined = (salt_b64 + password).encode("utf-8")
    digest = hashlib.new(HASH_NAME, combined).hexdigest()

    return salt_b64 + SEPARATOR + digest


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_credentials(
    username: str,
    password: str,
    stored_credentials: Dict[str, str],
) -> bool:
    """
    Verify a username/password pair against a stored credentials map.

    Parameters
    ----------
    username : str
        Non-empty username.
    password : str
        Non-empty plaintext password.
    stored_credentials : Dict[str, str]
        Mapping of username to ``salt$digest`` hash string.

    Returns
    -------
    bool
        ``True`` if the credentials match.

    Raises
    ------
    AuthenticationError
        If any input is invalid, the username is unknown, the stored
        entry is malformed, or the password does not match.
    """
    if not isinstance(username, str) or not username:
        raise AuthenticationError("username must be a non-empty string")

    if not isinstance(password, str) or not password:
        raise AuthenticationError("password must be a non-empty string")

    if not isinstance(stored_credentials, dict):
        raise AuthenticationError("stored_credentials must be a dictionary")

    if username not in stored_credentials:
        raise AuthenticationError("authentication failed")

    stored = stored_credentials[username]

    if not isinstance(stored, str) or SEPARATOR not in stored:
        raise AuthenticationError("stored credential is malformed")

    salt_b64, _, expected_digest = stored.partition(SEPARATOR)

    combined = (salt_b64 + password).encode("utf-8")
    computed_digest = hashlib.new(HASH_NAME, combined).hexdigest()

    if not hmac.compare_digest(computed_digest, expected_digest):
        raise AuthenticationError("authentication failed")

    return True


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def load_credentials(path: str) -> Dict[str, str]:
    """
    Load a username-to-hash mapping from a file.

    The expected format is one ``username=salt$digest`` pair per line.
    Blank lines and lines beginning with ``#`` are ignored.

    Parameters
    ----------
    path : str
        Path to the credentials file. ``~`` is expanded to the user's
        home directory.

    Returns
    -------
    Dict[str, str]
        Mapping of username to hash string.

    Raises
    ------
    AuthenticationError
        If ``path`` is invalid, the file cannot be read, or any line
        is malformed.
    """
    if not isinstance(path, str) or not path:
        raise AuthenticationError("path must be a non-empty string")

    expanded = os.path.expanduser(path)

    try:
        with open(expanded, "r", encoding="utf-8") as handle:
            raw = handle.read()
    except FileNotFoundError:
        raise AuthenticationError(f"credentials file not found: {expanded}")
    except PermissionError:
        raise AuthenticationError(f"permission denied: {expanded}")
    except OSError as exc:
        raise AuthenticationError(f"could not read credentials: {exc}")

    return _parse_credentials(raw)


def _parse_credentials(raw: str) -> Dict[str, str]:
    """
    Parse raw credentials text into a username-to-hash dictionary.

    Parameters
    ----------
    raw : str
        Raw file contents.

    Returns
    -------
    Dict[str, str]
        Mapping of username to hash string.

    Raises
    ------
    AuthenticationError
        If any non-blank, non-comment line is malformed or has an
        empty username or hash.
    """
    result: Dict[str, str] = {}

    lines = [
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    for line in lines:
        if "=" not in line:
            raise AuthenticationError(f"invalid credentials line: {line}")

        username, _, hashed = line.partition("=")
        username = username.strip()
        hashed = hashed.strip()

        if not username or not hashed:
            raise AuthenticationError(f"empty credential field: {line}")

        result[username] = hashed

    return result