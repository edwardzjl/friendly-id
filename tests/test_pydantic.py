#!/usr/bin/env python3
"""
Unittest-based tests for Pydantic integration with FriendlyID.

These tests verify that PydanticFriendlyID works correctly with Pydantic v2
for validation, serialization, and schema generation.
"""

import unittest
import uuid
import json
from typing import Optional

try:
    from pydantic import BaseModel, ValidationError
    from friendly_id.pydantic_types import PydanticFriendlyID

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # Dummy class for when Pydantic is not available

    # Create a dummy class for type annotations
    class PydanticFriendlyID:
        pass


from friendly_id import FriendlyID


@unittest.skipUnless(PYDANTIC_AVAILABLE, "Pydantic not available")
class TestPydanticIntegration(unittest.TestCase):
    """Test PydanticFriendlyID integration with Pydantic."""

    def setUp(self):
        """Set up test fixtures."""

        class User(BaseModel):
            """Example Pydantic model using PydanticFriendlyID."""

            id: PydanticFriendlyID
            name: str
            email: Optional[str] = None
            parent_id: Optional[PydanticFriendlyID] = None

        class UserResponse(BaseModel):
            """Nested model for testing."""

            user: User
            success: bool = True

        self.User = User
        self.UserResponse = UserResponse
        self.test_friendly_uuid = PydanticFriendlyID.from_friendly(
            "5wbwf6yUxVBcr48AMbz9cb"
        )

    def test_core_schema_method_exists(self):
        """Test that the core schema method exists for Pydantic v2."""
        self.assertTrue(hasattr(PydanticFriendlyID, "__get_pydantic_core_schema__"))
        self.assertTrue(
            callable(getattr(PydanticFriendlyID, "__get_pydantic_core_schema__"))
        )

    def test_json_schema_method_exists(self):
        """Test that the JSON schema method exists for Pydantic v2."""
        self.assertTrue(hasattr(PydanticFriendlyID, "__get_pydantic_json_schema__"))
        self.assertTrue(
            callable(getattr(PydanticFriendlyID, "__get_pydantic_json_schema__"))
        )

    def test_validation_with_friendly_uuid_instance(self):
        """Test validation with PydanticFriendlyID instance."""
        fuid = PydanticFriendlyID.random()
        user = self.User(id=fuid, name="John Doe")

        self.assertIsInstance(user.id, PydanticFriendlyID)
        self.assertEqual(user.id, fuid)
        self.assertEqual(user.name, "John Doe")

    def test_validation_with_base62_string(self):
        """Test validation with base62 string input."""
        base62_str = "5wbwf6yUxVBcr48AMbz9cb"
        user = self.User(id=base62_str, name="Jane Doe")

        self.assertIsInstance(user.id, PydanticFriendlyID)
        self.assertEqual(str(user.id), base62_str)

    def test_validation_with_uuid_string(self):
        """Test validation with standard UUID string."""
        regular_uuid = uuid.uuid4()
        uuid_str = str(regular_uuid)
        user = self.User(id=uuid_str, name="Bob Smith")

        self.assertIsInstance(user.id, PydanticFriendlyID)
        self.assertEqual(user.id.int, regular_uuid.int)

    def test_validation_with_uuid_object(self):
        """Test validation with UUID object."""
        regular_uuid = uuid.uuid4()
        user = self.User(id=regular_uuid, name="Alice Johnson")

        self.assertIsInstance(user.id, PydanticFriendlyID)
        self.assertEqual(user.id.int, regular_uuid.int)

    def test_validation_with_regular_friendly_uuid(self):
        """Test validation with regular FriendlyID instance."""
        regular_fuid = FriendlyID.random()
        user = self.User(id=regular_fuid, name="Charlie Brown")

        self.assertIsInstance(user.id, PydanticFriendlyID)
        self.assertEqual(user.id.int, regular_fuid.int)

    def test_validation_errors(self):
        """Test validation error handling."""
        invalid_inputs = [
            123,  # Integer
            12.34,  # Float
            [],  # List
            {},  # Dict
            None,  # None (when field is required)
            "invalid@string",  # Invalid string format
        ]

        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                with self.assertRaises(ValidationError):
                    self.User(id=invalid_input, name="Test")

    def test_serialization_to_dict(self):
        """Test serialization to dictionary."""
        user = self.User(
            id=self.test_friendly_uuid,
            name="Test User",
            email="test@example.com",
            parent_id=self.test_friendly_uuid,
        )

        user_dict = user.model_dump()

        # Check that IDs are still PydanticFriendlyID instances in dict
        self.assertIsInstance(user_dict["id"], PydanticFriendlyID)
        self.assertIsInstance(user_dict["parent_id"], PydanticFriendlyID)

        # Check values
        self.assertEqual(user_dict["name"], "Test User")
        self.assertEqual(user_dict["email"], "test@example.com")

    def test_serialization_to_json(self):
        """Test serialization to JSON."""
        user = self.User(
            id=self.test_friendly_uuid,
            name="Test User",
            email="test@example.com",
            parent_id=self.test_friendly_uuid,
        )

        json_str = user.model_dump_json()
        json_data = json.loads(json_str)

        # Check that IDs are serialized as base62 strings in JSON
        self.assertEqual(json_data["id"], str(self.test_friendly_uuid))
        self.assertEqual(json_data["parent_id"], str(self.test_friendly_uuid))

        # Check other values
        self.assertEqual(json_data["name"], "Test User")
        self.assertEqual(json_data["email"], "test@example.com")

    def test_round_trip_serialization(self):
        """Test round-trip serialization (model -> JSON -> model)."""
        original_user = self.User(
            id=self.test_friendly_uuid,
            name="Round Trip User",
            email="roundtrip@example.com",
        )

        # Serialize to JSON
        json_str = original_user.model_dump_json()

        # Deserialize from JSON
        reconstructed_user = self.User.model_validate_json(json_str)

        # Check that the round trip preserves the data
        self.assertEqual(original_user.id, reconstructed_user.id)
        self.assertEqual(original_user.name, reconstructed_user.name)
        self.assertEqual(original_user.email, reconstructed_user.email)

    def test_nested_models(self):
        """Test PydanticFriendlyID in nested Pydantic models."""
        user = self.User(
            id=PydanticFriendlyID.random(),
            name="Nested User",
            parent_id=self.test_friendly_uuid,
        )

        response = self.UserResponse(user=user, success=True)

        # Test serialization of nested model
        json_str = response.model_dump_json()
        json_data = json.loads(json_str)

        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["user"]["name"], "Nested User")
        self.assertIsInstance(json_data["user"]["id"], str)
        self.assertEqual(json_data["user"]["parent_id"], str(self.test_friendly_uuid))

    def test_json_schema_generation(self):
        """Test JSON schema generation includes FriendlyID metadata."""
        schema = self.User.model_json_schema()

        # Check that the schema exists
        self.assertIn("properties", schema)
        self.assertIn("id", schema["properties"])

        id_field_schema = schema["properties"]["id"]

        # Check that our custom schema metadata is included
        self.assertEqual(id_field_schema["type"], "string")
        self.assertEqual(id_field_schema["pattern"], "^[0-9A-Za-z]+$")
        self.assertIn("examples", id_field_schema)
        self.assertEqual(
            id_field_schema["description"], "A URL-friendly base62 encoded UUID"
        )

    def test_optional_fields(self):
        """Test handling of optional PydanticFriendlyID fields."""
        # Test with optional field provided
        user_with_parent = self.User(
            id=PydanticFriendlyID.random(),
            name="Child User",
            parent_id=self.test_friendly_uuid,
        )
        self.assertIsInstance(user_with_parent.parent_id, PydanticFriendlyID)

        # Test with optional field omitted
        user_without_parent = self.User(
            id=PydanticFriendlyID.random(), name="Root User"
        )
        self.assertIsNone(user_without_parent.parent_id)

    def test_model_validation_from_dict(self):
        """Test model validation from dictionary input."""
        data = {
            "id": str(self.test_friendly_uuid),
            "name": "Dict User",
            "email": "dict@example.com",
            "parent_id": str(self.test_friendly_uuid),
        }

        user = self.User.model_validate(data)

        self.assertIsInstance(user.id, PydanticFriendlyID)
        self.assertEqual(str(user.id), str(self.test_friendly_uuid))
        self.assertEqual(user.name, "Dict User")

    def test_architectural_separation(self):
        """Test that core FriendlyID doesn't have Pydantic methods."""
        # Core FriendlyID should NOT have Pydantic methods (clean separation)
        self.assertFalse(hasattr(FriendlyID, "__get_pydantic_core_schema__"))
        self.assertFalse(hasattr(FriendlyID, "__get_pydantic_json_schema__"))

        # PydanticFriendlyID SHOULD have Pydantic methods
        self.assertTrue(hasattr(PydanticFriendlyID, "__get_pydantic_core_schema__"))
        self.assertTrue(hasattr(PydanticFriendlyID, "__get_pydantic_json_schema__"))

    def test_inheritance_relationship(self):
        """Test that PydanticFriendlyID properly inherits from FriendlyID."""
        puid = PydanticFriendlyID.random()

        # Should be instance of all parent classes
        self.assertIsInstance(puid, PydanticFriendlyID)
        self.assertIsInstance(puid, FriendlyID)
        self.assertIsInstance(puid, uuid.UUID)

        # Should have the same string representation as core FriendlyID
        fuid = FriendlyID.from_uuid(puid.to_uuid())
        self.assertEqual(str(puid), str(fuid))


if __name__ == "__main__":
    # Print availability status
    if PYDANTIC_AVAILABLE:
        print("Pydantic is available - running full integration tests")
    else:
        print("Pydantic not available - running basic method tests only")
        print("Install Pydantic to run full tests: pip install pydantic")

    unittest.main(verbosity=2)
