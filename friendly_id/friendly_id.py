import uuid


# https://en.wikipedia.org/wiki/Base62
base62alphabet: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
base: int = len(base62alphabet)  # base62


def _encode_uuid_to_base62(uuid_obj: uuid.UUID) -> str:
    """Internal function to encode UUID to base62."""
    input_val = uuid_obj.int
    if input_val == 0:
        return "0"

    res = ""
    while input_val != 0:
        res += base62alphabet[input_val % base]
        input_val = input_val // base
    return res[::-1]


def _decode_base62_to_int(base62_str: str) -> int:
    """Internal function to decode base62 string to integer."""
    res = 0
    for c in base62_str:
        try:
            i = base62alphabet.index(c)
        except ValueError:
            raise ValueError(f"Invalid character '{c}' in base62 string")
        res = res * base + i
    return res


class FriendlyUUID(uuid.UUID):
    """
    A UUID subclass that uses base62 encoding for string representation.

    This class maintains full UUID functionality while providing a more
    human-friendly string representation using base62 encoding.
    """

    def __init__(
        self,
        hex: str = None,
        bytes: bytes = None,
        bytes_le: bytes = None,
        fields: tuple = None,
        int: int = None,
        version: int = None,
        *,
        friendly: str = None,
    ):
        """
        Initialize a FriendlyUUID.

        Accepts all standard UUID constructor arguments, plus:

        Args:
            friendly (str): A base62 encoded string to decode into a UUID

        All other arguments are the same as uuid.UUID constructor.
        """
        if friendly is not None:
            if any(arg is not None for arg in [hex, bytes, bytes_le, fields, int]):
                raise TypeError(
                    "Cannot specify both 'friendly' and other UUID arguments"
                )
            # Decode the friendly string to an integer
            uuid_int = _decode_base62_to_int(friendly)
            super().__init__(int=uuid_int, version=version)
        else:
            super().__init__(
                hex=hex,
                bytes=bytes,
                bytes_le=bytes_le,
                fields=fields,
                int=int,
                version=version,
            )

    @classmethod
    def from_uuid(cls, uuid_obj: uuid.UUID) -> "FriendlyUUID":
        """Create a FriendlyUUID from a standard UUID object."""
        return cls(int=uuid_obj.int)

    @classmethod
    def from_friendly(cls, friendly_str: str) -> "FriendlyUUID":
        """Create a FriendlyUUID from a base62 encoded string."""
        return cls(friendly=friendly_str)

    @classmethod
    def random(cls) -> "FriendlyUUID":
        """Generate a random FriendlyUUID (equivalent to uuid4)."""
        return cls.from_uuid(uuid.uuid4())

    def __str__(self) -> str:
        """Return the base62 encoded representation."""
        return _encode_uuid_to_base62(self)

    def __repr__(self) -> str:
        """Return a detailed representation showing both formats."""
        return f"FriendlyUUID('{self!s}', uuid='{super().__str__()}')"

    @property
    def friendly(self) -> str:
        """Get the base62 encoded string representation."""
        return str(self)

    @property
    def standard(self) -> str:
        """Get the standard UUID string representation."""
        return super().__str__()

    def to_uuid(self) -> uuid.UUID:
        """Convert to a standard UUID object."""
        return uuid.UUID(int=self.int)
