"""
Unit tests for credential hashing and verification.
"""

import pytest

from aethergrid.exceptions import AuthenticationError
from aethergrid.security import (
    SEPARATOR,
    hash_password,
    load_credentials,
    verify_credentials,
)


# ---------------------------------------------------------------------------
# Test 1 — Hash produces a two-part string
# ---------------------------------------------------------------------------

def test_hash_password_format():
    hashed = hash_password("secret")

    assert hashed.count(SEPARATOR) == 1

    salt_b64, _, digest = hashed.partition(SEPARATOR)

    assert salt_b64 != ""
    assert len(digest) == 64


# ---------------------------------------------------------------------------
# Test 2 — Two hashes of the same password differ (salted)
# ---------------------------------------------------------------------------

def test_hash_password_salted():
    a = hash_password("same_password")
    b = hash_password("same_password")

    assert a != b


# ---------------------------------------------------------------------------
# Test 3 — Verify accepts correct credentials
# ---------------------------------------------------------------------------

def test_verify_accepts_correct_credentials():
    stored = {"alice": hash_password("wonderland")}

    result = verify_credentials("alice", "wonderland", stored)

    assert result is True


# ---------------------------------------------------------------------------
# Test 4 — Verify rejects wrong password
# ---------------------------------------------------------------------------

def test_verify_rejects_wrong_password():
    stored = {"alice": hash_password("wonderland")}

    with pytest.raises(AuthenticationError):
        verify_credentials("alice", "wrong", stored)


# ---------------------------------------------------------------------------
# Test 5 — Verify rejects unknown user
# ---------------------------------------------------------------------------

def test_verify_rejects_unknown_user():
    stored = {"alice": hash_password("wonderland")}

    with pytest.raises(AuthenticationError):
        verify_credentials("bob", "wonderland", stored)


# ---------------------------------------------------------------------------
# Test 6 — Verify rejects malformed stored entry
# ---------------------------------------------------------------------------

def test_verify_rejects_malformed_stored_entry():
    stored = {"alice": "no_separator_in_this_string"}

    with pytest.raises(AuthenticationError):
        verify_credentials("alice", "wonderland", stored)


# ---------------------------------------------------------------------------
# Test 7 — Load credentials from a valid file
# ---------------------------------------------------------------------------

def test_load_credentials_valid(tmp_path):
    alice_hash = hash_password("wonderland")
    bob_hash = hash_password("builder")

    creds_file = tmp_path / "credentials.txt"
    creds_file.write_text(
        "# AetherGrid credentials\n"
        "\n"
        f"alice={alice_hash}\n"
        f"bob={bob_hash}\n",
        encoding="utf-8",
    )

    result = load_credentials(str(creds_file))

    assert "alice" in result
    assert "bob" in result
    assert result["alice"] == alice_hash
    assert result["bob"] == bob_hash


# ---------------------------------------------------------------------------
# Test 8 — Load credentials from a missing file raises
# ---------------------------------------------------------------------------

def test_load_credentials_missing_file_raises():
    with pytest.raises(AuthenticationError):
        load_credentials("this_file_does_not_exist.txt")


# ---------------------------------------------------------------------------
# Test 9 — Invalid inputs raise AuthenticationError
# ---------------------------------------------------------------------------

def test_hash_password_invalid_input_raises():
    with pytest.raises(AuthenticationError):
        hash_password("")

    with pytest.raises(AuthenticationError):
        hash_password(None)

    with pytest.raises(AuthenticationError):
        hash_password(42)


def test_verify_credentials_invalid_inputs_raise():
    stored = {"alice": hash_password("wonderland")}

    with pytest.raises(AuthenticationError):
        verify_credentials("", "wonderland", stored)

    with pytest.raises(AuthenticationError):
        verify_credentials("alice", "", stored)

    with pytest.raises(AuthenticationError):
        verify_credentials("alice", "wonderland", "not a dict")


def test_load_credentials_invalid_path_raises():
    with pytest.raises(AuthenticationError):
        load_credentials("")

    with pytest.raises(AuthenticationError):
        load_credentials(None)


# ---------------------------------------------------------------------------
# Test 10 — Malformed credentials file raises
# ---------------------------------------------------------------------------

def test_load_credentials_malformed_line_raises(tmp_path):
    creds_file = tmp_path / "bad.txt"
    creds_file.write_text(
        "valid=hash$value\n"
        "this_line_has_no_equals\n",
        encoding="utf-8",
    )

    with pytest.raises(AuthenticationError):
        load_credentials(str(creds_file))


def test_load_credentials_empty_field_raises(tmp_path):
    creds_file = tmp_path / "bad.txt"
    creds_file.write_text("=no_username\n", encoding="utf-8")

    with pytest.raises(AuthenticationError):
        load_credentials(str(creds_file))