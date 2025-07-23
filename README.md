# Friendly Id

> version 0.4.0

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
