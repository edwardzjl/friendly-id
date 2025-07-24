# Friendly Id

> version 0.5.0

[![test friendly-id](https://github.com/edwardzjl/friendly-id/actions/workflows/test.yml/badge.svg)](https://github.com/edwardzjl/friendly-id/actions/workflows/test.yml)

Inspired by [FriendlyID](https://github.com/Devskiller/friendly-id)

## What is the FriendlyId library?

The FriendlyID library provides a UUID subclass that uses base62 encoding for its string representation. It converts a given UUID (with 36 characters) to a URL-friendly ID (a "FriendlyUUID") which is based on Base62 (with a maximum of 22 characters), as in the example below:


    UUID                                        Friendly UUID

    c3587ec5-0976-497f-8374-61e0c2ea3da5   ->   5wbwf6yUxVBcr48AMbz9cb
    |                                           |                              
    36 characters                               22 characters or less

**FriendlyUUID extends the standard UUID class**, providing all the functionality of a regular UUID while displaying as a compact, URL-friendly string by default.

## Key Features

* **Full UUID compatibility**: FriendlyUUID is a true UUID subclass
* **Automatic friendly display**: `str(friendly_uuid)` returns the base62 format
* **Access to both formats**: `.friendly` property for base62, `.standard` property for UUID format
* **Drop-in replacement**: Works with existing code that expects UUID objects
* **Convert from a FriendlyUUID back to the original UUID format**
* **Create new, random FriendlyUUIDs**

## Why use a FriendlyUUID?

Universal Unique IDs (UUIDs) provide a non-sequential and unique identifier that can be generated separately from the source database. As a result, it is not possible to guess either the previous or next identifier. That's great, but, to achieve this level of security, a UUID is long (128 bits long) and looks ugly (36 alphanumeric characters including four hyphens which are added to make it easier to read the UUID), as in this example: `123e4567-e89b-12d3-a456-426655440000`.

Such a format is:

* difficult to read (especially if it is part of a URL)
* difficult to remember
* cannot be copied with just two mouse-clicks (you have to select manually the start and end positions)
* can easily become broken across lines when it is copied, pasted, edited, or sent.

FriendlyUUID library solves these problems by extending the standard UUID class and overriding its string representation to use Base62 with alphanumeric characters in the range [0-9A-Za-z] into a compact representation which consists of a maximum of 22 characters (but in fact often contains fewer characters).

## Usage

FriendlyId can be installed through PyPI:

```sh
python -m pip install friendly-id
```

### Basic Usage

Generate a random FriendlyUUID:

```python
from friendly_id import FriendlyUUID

# Generate a random FriendlyUUID
fuid = FriendlyUUID.random()
print(fuid)  # Prints base62 format, e.g., "5wbwf6yUxVBcr48AMbz9cb"
print(f"User ID: {fuid}")  # Perfect for URLs and display
```

Create from existing UUID:

```python
import uuid
from friendly_id import FriendlyUUID

# Convert existing UUID
regular_uuid = uuid.uuid4()
fuid = FriendlyUUID.from_uuid(regular_uuid)
print(fuid)  # Base62 format
```

Create from base62 string:

```python
from friendly_id import FriendlyUUID

# Create from friendly string
fuid = FriendlyUUID.from_friendly("5wbwf6yUxVBcr48AMbz9cb")
print(fuid.standard)  # c3587ec5-0976-497f-8374-61e0c2ea3da5
```

### Access Different Formats

```python
from friendly_id import FriendlyUUID

fuid = FriendlyUUID.random()

# Base62 format (default string representation)
print(str(fuid))       # e.g., "5wbwf6yUxVBcr48AMbz9cb"
print(fuid.friendly)   # Same as str(fuid)

# Standard UUID format
print(fuid.standard)   # e.g., "c3587ec5-0976-497f-8374-61e0c2ea3da5"

# Convert back to regular UUID
regular_uuid = fuid.to_uuid()
print(regular_uuid)    # Standard UUID object
```

### UUID Compatibility

Since FriendlyUUID extends UUID, it works everywhere a UUID is expected:

```python
import uuid
from friendly_id import FriendlyUUID

fuid = FriendlyUUID.random()

# All UUID properties and methods work
print(fuid.version)    # 4
print(fuid.hex)        # Hexadecimal representation
print(fuid.bytes)      # Bytes representation

# Type checking
isinstance(fuid, uuid.UUID)  # True
isinstance(fuid, FriendlyUUID)  # True

# Equality with regular UUIDs
regular_uuid = uuid.UUID(fuid.standard)
fuid == regular_uuid  # True

# Use in collections
uuid_set = {fuid, regular_uuid}  # Only one item (they're equal)
```

### Database Usage

```python
from friendly_id import FriendlyUUID

# For display/URLs (base62 format)
user_id = FriendlyUUID.random()
url = f"https://example.com/users/{user_id}"

# For database storage (standard UUID format)
db_value = user_id.standard
cursor.execute("INSERT INTO users (id, name) VALUES (%s, %s)", 
               (db_value, "John Doe"))

# Loading from database
loaded_uuid = FriendlyUUID(db_value)
print(loaded_uuid)  # Displays in friendly format
```

## SQLAlchemy Integration

FriendlyUUID includes seamless SQLAlchemy integration through an optional extra:

```sh
pip install friendly-id[sqlalchemy]
```

### FriendlyUUIDType

Stores UUIDs in the database's native UUID format while providing FriendlyUUID objects in Python:

```python
from sqlalchemy import Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from friendly_id import FriendlyUUID
from friendly_id.sqlalchemy_types import FriendlyUUIDType

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[FriendlyUUID] = mapped_column(
        FriendlyUUIDType, primary_key=True, insert_default=FriendlyUUID.random
    )
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)

# Usage
user = User(name="Alice", email="alice@example.com")
session.add(user)
session.commit()

print(user.id)  # Prints: 5wbwf6yUxVBcr48AMbz9cb (base62 format)
print(user.id.standard)  # Prints: c3587ec5-0976-497f-8374-61e0c2ea3da5

# Query by any format
alice = session.query(User).filter_by(id=user.id).first()  # FriendlyUUID
alice = session.query(User).filter_by(id=str(user.id)).first()  # base62 string
alice = session.query(User).filter_by(id=user.id.standard).first()  # UUID string
```

### Database Compatibility

FriendlyUUIDType automatically selects the optimal storage format for each database:

- **PostgreSQL**: Uses native UUID type for optimal performance and indexing
- **MySQL**: Uses CHAR(36) for UUID string storage
- **SQLite**: Uses TEXT for UUID string storage
- **Other databases**: Falls back to string storage

## Pydantic Integration

FriendlyUUID includes built-in Pydantic v2 support for seamless integration with Pydantic models. Install the optional extra for enhanced features:

```sh
pip install friendly-id[pydantic]
```

**Note**: This library requires Pydantic v2.0 or higher. Pydantic v1 is no longer supported.

### Basic Usage with Pydantic

```python
from pydantic import BaseModel
from friendly_id.pydantic_types import PydanticFriendlyUUID as FriendlyUUID

class User(BaseModel):
    id: FriendlyUUID
    name: str
    email: str

# Create from various input types
user1 = User(id=FriendlyUUID.random(), name="John", email="john@example.com")
user2 = User(id="5wbwf6yUxVBcr48AMbz9cb", name="Jane", email="jane@example.com")  # base62
user3 = User(id="c3587ec5-0976-497f-8374-61e0c2ea3da5", name="Bob", email="bob@example.com")  # UUID

# Serialization automatically uses base62 format
print(user1.model_dump_json())
# {"id": "7mkedUHZ3nyAx11JWbR91z", "name": "John", "email": "john@example.com"}
```

### Validation Features

FriendlyUUID automatically validates and converts:
- Existing FriendlyUUID instances (pass-through)
- Regular UUID objects
- Base62 strings
- Standard UUID strings
- Rejects invalid formats with clear error messages

### JSON Schema Support

FriendlyUUID provides proper JSON schema for OpenAPI generation:

```python
schema = User.model_json_schema()
# FriendlyUUID fields include:
# - type: "string"
# - pattern: "^[0-9A-Za-z]+$" (base62 validation)
# - description: "A URL-friendly base62 encoded UUID"
```

## Performance

FriendlyUUID involves a trade-off between CPU overhead and I/O efficiency:

- **CPU**: ~6x slower base62 encoding (~3 microseconds per ID)
- **I/O**: 39% bandwidth savings (22 vs 36 characters)
- **Database**: Uses native UUID storage (no storage overhead)

Run the included benchmark to see detailed performance analysis:
```bash
python benchmark.py --count 1000
```

For detailed performance analysis, see [PERFORMANCE.md](PERFORMANCE.md).

## Choosing Between FriendlyUUID and Standard UUID

FriendlyUUID presents a clear trade-off: **3 microseconds CPU overhead vs 14 characters I/O savings per ID**.

### Consider FriendlyUUID when:
- Network bandwidth or data transfer costs are significant
- User-facing URLs and identifiers matter for UX  
- Text-based logging and data export are frequent
- Web APIs where transfer size matters
- Mobile applications with bandwidth constraints

### Consider Standard UUID when:
- High-frequency serialization with minimal I/O
- CPU resources are constrained or critical
- Existing systems require standard UUID format
- Microsecond-level performance is essential
- Real-time systems where every cycle counts

### Evaluation Factors
Consider your application's specific characteristics:
- **I/O vs CPU ratio**: How much network/text processing vs computation?
- **Scale**: Volume of UUID operations vs data transmission
- **Constraints**: CPU limitations vs bandwidth costs
- **User experience**: Does identifier readability matter?
- **Integration**: Compatibility with existing systems

Run the benchmark with your expected workload to get concrete numbers for your specific use case.

## Breaking Changes

**⚠️ Important**: 0.4.0 introduces breaking changes from previous versions:

- `str(FriendlyUUID)` now returns base62 format instead of standard UUID format
- Use `.standard` property when you need the standard UUID string format
- JSON serialization will use base62 format by default
- Update any code that expects `str(uuid)` to return standard UUID format

## Migration Guide

If you were using the previous functional API:

```python
# Old way (no longer available)
from friendly_id import friendly_id, encode, decode

id_str = friendly_id()
encoded = encode(some_uuid)
decoded = decode(some_string)

# New way
from friendly_id import FriendlyUUID

id_str = str(FriendlyUUID.random())
encoded = str(FriendlyUUID.from_uuid(some_uuid))
decoded = FriendlyUUID.from_friendly(some_string).to_uuid()
```
