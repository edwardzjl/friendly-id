"""
Tests for SQLAlchemy integration with FriendlyUUID.

These tests require SQLAlchemy to be installed:
    pip install friendly-id[sqlalchemy]
"""

import unittest
import uuid
from unittest.mock import Mock

try:
    from sqlalchemy import create_engine, Integer, Text
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
    from sqlalchemy.exc import StatementError

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

if SQLALCHEMY_AVAILABLE:
    from friendly_id import FriendlyUUID
    from friendly_id.sqlalchemy_types import (
        FriendlyUUIDType,
    )


@unittest.skipUnless(SQLALCHEMY_AVAILABLE, "SQLAlchemy not available")
class TestFriendlyUUIDSQLAlchemy(unittest.TestCase):
    """Test SQLAlchemy integration with FriendlyUUID."""

    def setUp(self):
        """Set up test database and tables."""
        # Use in-memory SQLite for testing
        self.engine = create_engine("sqlite:///:memory:", echo=False)

        class Base(DeclarativeBase):
            pass

        self.Base = Base

        # Define test models
        class User(Base):
            __tablename__ = "users"
            id: Mapped[FriendlyUUID] = mapped_column(
                FriendlyUUIDType, primary_key=True, insert_default=FriendlyUUID.random
            )
            name: Mapped[str] = mapped_column(Text)
            email: Mapped[str] = mapped_column(Text)

        self.User = User

        # Create tables
        Base.metadata.create_all(self.engine)

        # Create sessionmaker
        self.sessionmaker = sessionmaker(bind=self.engine)

        # Test data
        self.test_uuid = uuid.UUID("c3587ec5-0976-497f-8374-61e0c2ea3da5")
        self.test_friendly_uuid = FriendlyUUID.from_uuid(self.test_uuid)
        self.test_base62 = "5wbwf6yUxVBcr48AMbz9cb"

    def test_friendly_uuid_type_creation(self):
        """Test creating and retrieving records with FriendlyUUIDType."""
        # Create user with FriendlyUUID
        user = self.User(
            id=self.test_friendly_uuid, name="John Doe", email="john@example.com"
        )

        with self.sessionmaker() as session:
            session.add(user)
            session.commit()

            # Retrieve user
            retrieved_user = session.query(self.User).filter_by(name="John Doe").first()

        self.assertIsNotNone(retrieved_user)
        self.assertIsInstance(retrieved_user.id, FriendlyUUID)
        self.assertEqual(retrieved_user.id, self.test_friendly_uuid)
        self.assertEqual(str(retrieved_user.id), self.test_base62)

    def test_friendly_uuid_type_with_regular_uuid(self):
        """Test that FriendlyUUIDType can handle regular UUID input."""
        # Create user with regular UUID
        user = self.User(id=self.test_uuid, name="Jane Doe", email="jane@example.com")
        with self.sessionmaker() as session:
            session.add(user)
            session.commit()

            # Retrieve user
            retrieved_user = session.query(self.User).filter_by(name="Jane Doe").first()

        self.assertIsNotNone(retrieved_user)
        self.assertIsInstance(retrieved_user.id, FriendlyUUID)
        self.assertEqual(retrieved_user.id.to_uuid(), self.test_uuid)

    def test_friendly_uuid_type_with_string_input(self):
        """Test that FriendlyUUIDType can handle string input."""
        # Test with UUID string
        user = self.User(id=str(self.test_uuid), name="User", email="user@example.com")

        with self.sessionmaker() as session:
            session.add(user)
            session.commit()

            # Retrieve users
            retrieved_user = session.query(self.User).filter_by(name="User").first()

        self.assertIsNotNone(retrieved_user)
        self.assertIsInstance(retrieved_user.id, FriendlyUUID)
        self.assertEqual(retrieved_user.id.to_uuid(), self.test_uuid)

    def test_querying_by_friendly_uuid(self):
        """Test querying records using FriendlyUUID."""
        # Create a user
        user = self.User(
            id=self.test_friendly_uuid, name="Query User", email="query@example.com"
        )

        with self.sessionmaker() as session:
            session.add(user)
            session.commit()

        with self.sessionmaker() as session:
            # Query by FriendlyUUID
            retrieved_user = (
                session.query(self.User).filter_by(id=self.test_friendly_uuid).first()
            )
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.name, "Query User")

        with self.sessionmaker() as session:
            # Query by regular UUID (should also work)
            retrieved_user2 = (
                session.query(self.User).filter_by(id=self.test_uuid).first()
            )
        self.assertIsNotNone(retrieved_user2)
        self.assertEqual(retrieved_user2.name, "Query User")

        with self.sessionmaker() as session:
            # Query by string representations
            retrieved_user3 = (
                session.query(self.User).filter_by(id=str(self.test_uuid)).first()
            )
            retrieved_user4 = (
                session.query(self.User).filter_by(id=self.test_base62).first()
            )

        self.assertIsNotNone(retrieved_user3)
        self.assertIsNotNone(retrieved_user4)
        self.assertEqual(retrieved_user3.name, "Query User")
        self.assertEqual(retrieved_user4.name, "Query User")

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid string input
        with self.assertRaises(StatementError):
            user = self.User(id="invalid-uuid-string", name="Error User")
            with self.sessionmaker() as session:
                session.add(user)
                session.flush()  # Force the conversion

        # Test invalid type input
        with self.assertRaises(StatementError):
            user = self.User(id=12345, name="Error User")
            with self.sessionmaker() as session:
                session.add(user)
                session.flush()

    def test_none_handling(self):
        """Test handling of None values."""

        # Create table that allows NULL
        class OptionalUser(self.Base):
            __tablename__ = "optional_users"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
            uuid_field: Mapped[FriendlyUUID | None] = mapped_column(
                FriendlyUUIDType, nullable=True
            )
            name: Mapped[str] = mapped_column(Text)

        self.Base.metadata.create_all(self.engine)

        # Create user with None UUID
        user = OptionalUser(uuid_field=None, name="No UUID User")
        with self.sessionmaker() as session:
            session.add(user)
            session.commit()

            # Retrieve and check
            retrieved_user = (
                session.query(OptionalUser).filter_by(name="No UUID User").first()
            )
        self.assertIsNone(retrieved_user.uuid_field)


@unittest.skipUnless(SQLALCHEMY_AVAILABLE, "SQLAlchemy not available")
class TestFriendlyUUIDTypeDialects(unittest.TestCase):
    """Test FriendlyUUIDType behavior with different database dialects."""

    def setUp(self):
        """Set up mock dialects for testing."""
        self.uuid_type = FriendlyUUIDType()
        self.test_uuid = uuid.UUID("c3587ec5-0976-497f-8374-61e0c2ea3da5")
        self.test_friendly_uuid = FriendlyUUID.from_uuid(self.test_uuid)

    def test_postgresql_dialect(self):
        """Test behavior with PostgreSQL dialect."""
        # Mock PostgreSQL dialect
        mock_dialect = Mock()
        mock_dialect.name = "postgresql"

        # Test bind param processing
        result = self.uuid_type.process_bind_param(
            self.test_friendly_uuid, mock_dialect
        )
        self.assertIsInstance(result, uuid.UUID)
        self.assertEqual(result, self.test_uuid)

        # Test result processing
        result = self.uuid_type.process_result_value(self.test_uuid, mock_dialect)
        self.assertIsInstance(result, FriendlyUUID)
        self.assertEqual(result, self.test_friendly_uuid)

    def test_sqlite_dialect(self):
        """Test behavior with SQLite dialect."""
        # Mock SQLite dialect
        mock_dialect = Mock()
        mock_dialect.name = "sqlite"

        # Test bind param processing
        result = self.uuid_type.process_bind_param(
            self.test_friendly_uuid, mock_dialect
        )
        self.assertEqual(result, str(self.test_uuid))

        # Test result processing
        result = self.uuid_type.process_result_value(str(self.test_uuid), mock_dialect)
        self.assertIsInstance(result, FriendlyUUID)
        self.assertEqual(result, self.test_friendly_uuid)

    def test_mysql_dialect(self):
        """Test behavior with MySQL dialect."""
        # Mock MySQL dialect
        mock_dialect = Mock()
        mock_dialect.name = "mysql"

        # Test bind param processing
        result = self.uuid_type.process_bind_param(
            self.test_friendly_uuid, mock_dialect
        )
        self.assertEqual(result, str(self.test_uuid))

        # Test result processing
        result = self.uuid_type.process_result_value(str(self.test_uuid), mock_dialect)
        self.assertIsInstance(result, FriendlyUUID)
        self.assertEqual(result, self.test_friendly_uuid)


if __name__ == "__main__":
    if not SQLALCHEMY_AVAILABLE:
        print(
            "SQLAlchemy not available. Install with: pip install friendly-id[sqlalchemy]"
        )
    else:
        unittest.main(verbosity=2)
