from unittest.mock import patch

import pytest

from schemalock import LockExistsError, SchemaDriftError, check, lock, lock_update


def test_lock_then_check_ok(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    assert check(pandas_df, name="customer_silver", dir=lock_dir) is True


def test_lock_twice_raises(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    with pytest.raises(LockExistsError):
        lock(pandas_df, name="customer_silver", dir=lock_dir)


def test_check_detects_dropped_column(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    dropped = pandas_df.drop(columns=["email"])
    with pytest.raises(SchemaDriftError) as excinfo:
        check(dropped, name="customer_silver", dir=lock_dir)
    assert "email" in str(excinfo.value)


def test_check_detects_new_column(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    added = pandas_df.copy()
    added["new_col"] = "x"
    with pytest.raises(SchemaDriftError) as excinfo:
        check(added, name="customer_silver", dir=lock_dir)
    assert "new_col" in str(excinfo.value)


def test_check_detects_retyped_column(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    retyped = pandas_df.copy()
    retyped["customer_id"] = retyped["customer_id"].astype(str)
    with pytest.raises(SchemaDriftError) as excinfo:
        check(retyped, name="customer_silver", dir=lock_dir)
    assert "customer_id" in str(excinfo.value)


def test_lock_update_requires_tty(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    with patch("sys.stdin.isatty", return_value=False):
        with pytest.raises(RuntimeError):
            lock_update(pandas_df, name="customer_silver", dir=lock_dir, reason="test")


def test_lock_update_writes_reason(pandas_df, lock_dir):
    from schemalock.serialize import read_lock

    lock(pandas_df, name="customer_silver", dir=lock_dir)
    added = pandas_df.copy()
    added["new_col"] = "x"

    with patch("sys.stdin.isatty", return_value=True), patch(
        "builtins.input", return_value="customer_silver"
    ):
        lock_update(added, name="customer_silver", dir=lock_dir, reason="added new_col")

    updated = read_lock("customer_silver", lock_dir)
    assert updated["reason"] == "added new_col"
    assert "new_col" in updated["columns"]


def test_lock_update_wrong_confirmation_aborts(pandas_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    with patch("sys.stdin.isatty", return_value=True), patch(
        "builtins.input", return_value="wrong_name"
    ):
        with pytest.raises(RuntimeError):
            lock_update(pandas_df, name="customer_silver", dir=lock_dir, reason="test")
