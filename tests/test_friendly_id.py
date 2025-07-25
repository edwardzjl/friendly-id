import unittest
import uuid

from friendly_id import FriendlyID


class TestFriendlyID(unittest.TestCase):
    """Test cases for FriendlyID class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_uuid_str = "c3587ec5-0976-497f-8374-61e0c2ea3da5"
        self.test_base62_str = "5wbwf6yUxVBcr48AMbz9cb"
        self.test_uuid = uuid.UUID(self.test_uuid_str)

    def test_basic_functionality(self):
        """Test basic FriendlyID functionality."""
        # Create random FriendlyID
        fuid = FriendlyID.random()
        self.assertIsInstance(fuid, FriendlyID)
        self.assertIsInstance(fuid, uuid.UUID)

        # Test properties exist
        self.assertTrue(hasattr(fuid, "friendly"))
        self.assertTrue(hasattr(fuid, "standard"))

        # Create from standard UUID
        regular_uuid = uuid.uuid4()
        fuid2 = FriendlyID.from_uuid(regular_uuid)
        self.assertEqual(fuid2.int, regular_uuid.int)
        self.assertIsInstance(fuid2, FriendlyID)

    def test_string_behavior(self):
        """Test how string operations work."""
        fuid = FriendlyID.from_friendly(self.test_base62_str)

        # Test string representation
        self.assertEqual(str(fuid), self.test_base62_str)
        self.assertEqual(fuid.friendly, self.test_base62_str)
        self.assertEqual(fuid.standard, self.test_uuid_str)

        # Test string operations
        friendly_str = str(fuid)
        self.assertTrue(friendly_str.upper().isupper())

        # Test in f-string formatting
        url = f"https://example.com/user/{fuid}"
        self.assertIn(self.test_base62_str, url)

    def test_uuid_compatibility(self):
        """Test compatibility with UUID operations."""
        fuid = FriendlyID.random()

        # Test UUID properties and methods work
        self.assertIn(fuid.version, [1, 3, 4, 5])  # Valid UUID versions
        self.assertIsNotNone(fuid.variant)
        self.assertIsInstance(fuid.int, int)
        self.assertIsInstance(fuid.hex, str)
        self.assertIsInstance(fuid.bytes, bytes)

        # Test conversion back to regular UUID
        regular_uuid = fuid.to_uuid()
        self.assertIsInstance(regular_uuid, uuid.UUID)
        self.assertEqual(fuid.int, regular_uuid.int)
        self.assertNotIsInstance(regular_uuid, FriendlyID)  # Should be plain UUID

    def test_creation_methods(self):
        """Test different ways to create FriendlyID."""
        # From friendly string
        fuid1 = FriendlyID(friendly=self.test_base62_str)
        self.assertEqual(str(fuid1), self.test_base62_str)

        # From hex string
        fuid2 = FriendlyID(self.test_uuid_str)
        self.assertEqual(fuid2.standard, self.test_uuid_str)

        # From int
        test_int = 260042770682645658313644171649588724135  # Corresponds to test UUID
        fuid3 = FriendlyID(int=test_int)
        self.assertIsInstance(fuid3, FriendlyID)

        # Check that fuid1 and fuid2 are the same
        self.assertEqual(fuid1, fuid2)
        self.assertEqual(fuid1.int, fuid2.int)

        # Test class methods
        fuid4 = FriendlyID.from_friendly(self.test_base62_str)
        fuid5 = FriendlyID.from_uuid(self.test_uuid)
        self.assertEqual(fuid4, fuid5)

    def test_collections(self):
        """Test using FriendlyID in collections."""
        # Test in sets
        fuids = {FriendlyID.random() for _ in range(3)}
        self.assertEqual(len(fuids), 3)  # Should be 3 unique items

        # Test as dictionary keys
        data = {FriendlyID.random(): f"User {i}" for i in range(3)}
        self.assertEqual(len(data), 3)

        # Test that all keys are FriendlyID instances
        for key in data.keys():
            self.assertIsInstance(key, FriendlyID)
            self.assertIsInstance(key, uuid.UUID)

    def test_comparison_with_regular_uuid(self):
        """Test how FriendlyID compares with regular UUID."""
        regular_uuid = uuid.UUID(self.test_uuid_str)
        friendly_id = FriendlyID(self.test_uuid_str)

        # Test equality
        self.assertEqual(friendly_id, regular_uuid)
        self.assertEqual(regular_uuid, friendly_id)

        # Test isinstance
        self.assertIsInstance(friendly_id, uuid.UUID)
        self.assertIsInstance(friendly_id, FriendlyID)
        self.assertNotIsInstance(regular_uuid, FriendlyID)

        # Test in sets (should be treated as same object)
        uuid_set = {regular_uuid, friendly_id}
        self.assertEqual(len(uuid_set), 1)  # Should deduplicate to 1 item

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid friendly string
        with self.assertRaises(ValueError):
            FriendlyID(friendly="invalid@string")

        # Test invalid UUID string
        with self.assertRaises(ValueError):
            FriendlyID("not-a-uuid")

        # Test conflicting arguments
        with self.assertRaises(TypeError):
            FriendlyID(self.test_uuid_str, friendly=self.test_base62_str)

    def test_round_trip_conversion(self):
        """Test that encoding and decoding preserves the original UUID."""
        original_uuid = uuid.uuid4()

        # Convert to FriendlyID and back
        friendly_id = FriendlyID.from_uuid(original_uuid)
        converted_back = friendly_id.to_uuid()

        self.assertEqual(original_uuid, converted_back)
        self.assertEqual(original_uuid.int, friendly_id.int)

        # Test with base62 string
        base62_str = str(friendly_id)
        from_base62 = FriendlyID.from_friendly(base62_str)
        self.assertEqual(original_uuid, from_base62)

    def test_edge_cases(self):
        """Test edge cases like min/max UUID values."""
        # Test zero UUID
        zero_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        fuid_zero = FriendlyID.from_uuid(zero_uuid)
        self.assertEqual(str(fuid_zero), "0")
        self.assertEqual(fuid_zero.to_uuid(), zero_uuid)

        # Test max UUID
        max_uuid = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
        fuid_max = FriendlyID.from_uuid(max_uuid)
        self.assertEqual(fuid_max.to_uuid(), max_uuid)

        # Test that base62 strings are reasonable length
        self.assertLessEqual(len(str(fuid_max)), 22)


if __name__ == "__main__":
    unittest.main(verbosity=2)
