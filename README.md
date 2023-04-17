# Friendly Id

> version 0.3.1

Inspired by [FriendlyID](https://github.com/Devskiller/friendly-id)

What is the FriendlyId library?
--
The FriendlyId library converts a given UUID (with 36 characters) to a URL-friendly ID (a "FriendlyId") which is based on Base62 (with a maximum of 22 characters), as in the example below:


    UUID                                        Friendly ID

    c3587ec5-0976-497f-8374-61e0c2ea3da5   ->   5wbwf6yUxVBcr48AMbz9cb
    |                                           |                              
    36 characters                               22 characters or less

In addition, this library allows to:


* convert from a FriendlyId back to the original UUID; and
* create a new, random FriendlyId

Why use a FriendlyId?
--
Universal Unique IDs (UUIDs) provide a non-sequential and unique identifier that can be generated separately from the source database. As a result, it is not possible to guess either the previous or next identifier. That's great, but, to achieve this level of security, a UUID is long (128 bits long) and looks ugly (36 alphanumeric characters including four hyphens which are added to make it easier to read the UUID), as in this example: `123e4567-e89b-12d3-a456-426655440000`.

Such a format is:

* difficult to read (especially if it is part of a URL)
* difficult to remember
* cannot be copied with just two mouse-clicks (you have to select manually the start and end positions)
* can easily become broken across lines when it is copied, pasted, edited, or sent.

FriendlyId library solves these problems by converting a given UUID using Base62 with alphanumeric characters in the range [0-9A-Za-z] into a FriendlyId which consists of a maximum of 22 characters (but in fact often contains fewer characters).

Usage
---

Python Package
----
FriendlyId can be installed through PyPI:

```bash
python -m pip install friendly-id
```

Generate a FriendlyId
```python
from friendly_id import friendly_id

id: str = friendly_id(),
```

Convert UUID to FriendlyId
```python
import uuid
from friendly_id import encode

uid = uuid.uuid4()
id: str = encode(uid),
```
