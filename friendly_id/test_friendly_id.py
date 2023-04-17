import unittest

import uuid
from friendly_id.friendly_id import encode, decode

class FriendlyIdTestCase(unittest.TestCase):

    def test_encode(self):
        res = encode(uuid.UUID("c910c385-0486-4eb5-b7fb-f001ac5039e7"))
        self.assertEqual("67P7MaJ0NANEBRW3aXfGJ5", res)

    def test_decode(self):
        id = decode("67P7MaJ0NANEBRW3aXfGJ5")
        self.assertEqual(uuid.UUID("c910c385-0486-4eb5-b7fb-f001ac5039e7"), id)
