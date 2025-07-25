"""
Pydantic integration for FriendlyID.

This module provides Pydantic-compatible types for working with FriendlyID
in Pydantic models. The PydanticFriendlyID extends FriendlyID with
proper Pydantic v2 validation and serialization support.

To use this module, install with the pydantic extra:
    pip install friendly-id[pydantic]
"""

try:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema, core_schema
    from pydantic.json_schema import GetJsonSchemaHandler, JsonSchemaValue
except ImportError:
    raise ImportError(
        "Pydantic is required for this module. "
        "Install with: pip install friendly-id[pydantic]"
    )

import uuid
from typing import Any

from .friendly_id import FriendlyID


class PydanticFriendlyID(FriendlyID):
    """
    A Pydantic-compatible FriendlyID that provides proper validation
    and serialization for Pydantic v2 models.

    This class extends FriendlyID with Pydantic-specific methods for
    validation, serialization, and JSON schema generation.

    Example:
        from friendly_id.pydantic_types import PydanticFriendlyID as FriendlyID
        from pydantic import BaseModel

        class User(BaseModel):
            id: FriendlyID
            name: str
            email: str | None = None

        # Create from various input types
        user1 = User(id=FriendlyID.random(), name="John")
        user2 = User(id="5wbwf6yUxVBcr48AMbz9cb", name="Jane")  # base62
        user3 = User(id="c3587ec5-0976-497f-8374-61e0c2ea3da5", name="Bob")  # UUID

        # Serialization uses base62 format
        print(user1.model_dump_json())
        # {"id": "7mkedUHZ3nyAx11JWbR91z", "name": "John", "email": null}
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Pydantic v2 core schema for validation and serialization.

        Returns a core schema that accepts FriendlyID instances, regular UUID
        objects, base62 strings, and standard UUID strings, converting them all
        to PydanticFriendlyID instances.
        """

        def validate_friendly_uuid(value: Any) -> "PydanticFriendlyID":
            """Validate and convert input to PydanticFriendlyID."""
            if isinstance(value, cls):
                return value
            elif isinstance(value, FriendlyID):
                # Convert FriendlyID to PydanticFriendlyID
                return cls.from_uuid(value.to_uuid())
            elif isinstance(value, uuid.UUID):
                return cls.from_uuid(value)
            elif isinstance(value, str):
                # Try base62 first, then UUID string
                try:
                    return cls.from_friendly(value)
                except ValueError:
                    try:
                        return cls.from_uuid(uuid.UUID(value))
                    except ValueError:
                        raise ValueError(f"Invalid FriendlyID format: {value}")
            else:
                raise ValueError(
                    f"PydanticFriendlyID expected str or UUID, got {type(value)}"
                )

        # Create a union schema that accepts multiple input types
        return core_schema.union_schema(
            [
                # Accept existing PydanticFriendlyID instances (pass through)
                core_schema.is_instance_schema(cls),
                # Accept strings and convert them
                core_schema.no_info_after_validator_function(
                    validate_friendly_uuid, core_schema.str_schema()
                ),
                # Accept UUID instances and convert them
                core_schema.no_info_after_validator_function(
                    validate_friendly_uuid, core_schema.is_instance_schema(uuid.UUID)
                ),
                # Accept FriendlyID instances and convert them
                core_schema.no_info_after_validator_function(
                    validate_friendly_uuid, core_schema.is_instance_schema(FriendlyID)
                ),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """
        Customize the JSON schema for Pydantic v2.

        This method provides proper JSON schema metadata for OpenAPI generation,
        including the base62 pattern, examples, and description.
        """
        json_schema = handler(core_schema)
        json_schema.update(
            type="string",
            pattern="^[0-9A-Za-z]+$",  # Base62 pattern
            examples=["5wbwf6yUxVBcr48AMbz9cb"],
            description="A URL-friendly base62 encoded UUID",
        )
        return json_schema
