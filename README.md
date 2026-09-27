# schemalock

A git-trackable lockfile for DataFrame schemas — like `poetry.lock`, but for schemas.

Detects unintended schema drift in data pipelines and requires deliberate,
confirmed action to update. Works universally across pandas, PySpark (local),
and PySpark on Databricks.

## Install

```bash
pip install schemalock
# or, with local PySpark support:
pip install schemalock[spark]
```

## Usage

```python
from schemalock import lock, check, lock_update

# Create a lock file (fails if one already exists)
lock(df, name="customer_silver")

# Validate a dataframe's schema against the lock file
check(df, name="customer_silver")  # raises SchemaDriftError on mismatch

# Deliberately update the lock file (interactive only)
lock_update(df, name="customer_silver")
```

## How it works

`schemalock` computes a normalized schema for a pandas or PySpark DataFrame —
mapping engine-specific types (`int64`, `LongType()`, ...) into a shared
vocabulary (`integer`, `float`, `string`, `timestamp`, `boolean`, ...) — and
writes it to a JSON lock file under `schemas/`. Future runs of `check()`
compare the current schema against the lock file and raise `SchemaDriftError`
on any mismatch.

Lock files can only be created once (`lock()`), and can only be changed via
`lock_update()`, which requires an interactive TTY, a typed confirmation of
the schema name, and a non-empty reason.

## License

MIT
