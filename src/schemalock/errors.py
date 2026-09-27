class SchemaLockError(Exception):
    """Base class for all schemalock errors."""


class SchemaDriftError(SchemaLockError):
    """Raised by check() when the dataframe's schema no longer matches the lock file."""


class LockExistsError(SchemaLockError):
    """Raised by lock() when a lock file already exists for the given name."""
