"""
SQLAlchemy integration for FriendlyUUID.

This module provides SQLAlchemy type decorators for working with FriendlyUUID
in database operations. The FriendlyUUID is stored as a native UUID in the
database (for optimal performance and indexing) but automatically converted
to/from FriendlyUUID objects in Python code.

To use this module, install with the sqlalchemy extra:
    pip install friendly-id[sqlalchemy]
"""

try:
    from sqlalchemy import types
    from sqlalchemy.dialects import postgresql, mysql, sqlite
    from sqlalchemy.engine import Dialect
except ImportError:
    raise ImportError(
        "SQLAlchemy is required for this module. "
        "Install with: pip install friendly-id[sqlalchemy]"
    )

import uuid

from .friendly_id import FriendlyUUID


class FriendlyUUIDType(types.TypeDecorator):
    """
    A SQLAlchemy type that stores FriendlyUUID as UUID in the database
    but automatically converts to/from FriendlyUUID in Python.

    This type uses the database's native UUID type when available,
    falling back to string storage for databases that don't support UUID.

    Example:
        class User(Base):
            __tablename__ = 'users'
            id: Mapped[FriendlyUUID] = mapped_column(
                FriendlyUUIDType,
                primary_key=True,
                insert_default=FriendlyUUID.random
            )
            name: Mapped[str] = mapped_column(Text)

        # Creating a user
        user = User(id=FriendlyUUID.random(), name="John Doe")
        session.add(user)
        session.commit()

        # Querying - id will be a FriendlyUUID instance
        user = session.query(User).first()
        print(user.id)  # Prints base62 format
        print(user.id.standard)  # Prints UUID format
    """

    impl = types.TypeEngine
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> types.TypeEngine:
        """Load the appropriate implementation for the given dialect."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())
        elif dialect.name == "mysql":
            # MySQL 8.0+ supports UUID as BINARY(16), older versions use CHAR(36)
            return dialect.type_descriptor(mysql.CHAR(36))
        elif dialect.name == "sqlite":
            # SQLite doesn't have native UUID, use TEXT
            return dialect.type_descriptor(sqlite.TEXT())
        else:
            # Default to string for other databases
            return dialect.type_descriptor(types.String(36))

    def process_bind_param(
        self, value: FriendlyUUID | uuid.UUID | str | None, dialect: Dialect
    ) -> uuid.UUID | str | None:
        """Convert Python value to database value."""
        if value is None:
            return None

        if isinstance(value, FriendlyUUID):
            # Convert FriendlyUUID to appropriate database format
            if dialect.name == "postgresql":
                return value.to_uuid()
            else:
                return value.standard
        elif isinstance(value, uuid.UUID):
            # Handle regular UUID
            if dialect.name == "postgresql":
                return value
            else:
                return str(value)
        elif isinstance(value, str):
            # Handle string input - could be UUID string or base62
            try:
                # Try to parse as FriendlyUUID (base62)
                fuid = FriendlyUUID.from_friendly(value)
                if dialect.name == "postgresql":
                    return fuid.to_uuid()
                else:
                    return fuid.standard
            except ValueError:
                try:
                    # Try to parse as regular UUID
                    regular_uuid = uuid.UUID(value)
                    if dialect.name == "postgresql":
                        return regular_uuid
                    else:
                        return str(regular_uuid)
                except ValueError:
                    raise ValueError(f"Invalid UUID or FriendlyUUID string: {value}")
        else:
            raise TypeError(
                f"Expected FriendlyUUID, UUID, or string, got {type(value)}"
            )

    def process_result_value(
        self, value: uuid.UUID | str | None, dialect: Dialect
    ) -> FriendlyUUID | None:
        """Convert database value to Python value."""
        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            # PostgreSQL returns UUID objects
            return FriendlyUUID.from_uuid(value)
        elif isinstance(value, str):
            # Other databases return strings
            try:
                regular_uuid = uuid.UUID(value)
                return FriendlyUUID.from_uuid(regular_uuid)
            except ValueError:
                raise ValueError(f"Invalid UUID string from database: {value}")
        else:
            raise TypeError(f"Unexpected database value type: {type(value)}")
