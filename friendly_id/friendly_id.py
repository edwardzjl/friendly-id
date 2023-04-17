import uuid


# https://en.wikipedia.org/wiki/Base62
base62alphabet: str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
base: int = len(base62alphabet) # base62

def friendly_id() -> str:
    id = uuid.uuid4()
    return encode(id)

def encode(raw: uuid.UUID) -> str:
    """
    ConvertUp converts a hexadecimal UUID string to a base alphabet greater than
    16. It is used here to compress a 32 character UUID down to 23 URL friendly characters.

    Args:
        raw (str): _description_
        mask (str): _description_

    Returns:
        str: _description_
    """
    
    input = raw.int
    res = ''
    while input != 0:
        res += base62alphabet[input % base]
        input = input // base
    return res[::-1]

def decode(raw: str) -> uuid.UUID:
    res = 0
    for c in raw:
        try:
            i = base62alphabet.index(c)
        except ValueError:
            raise ValueError('Invalid character in base62 string')
        res = res * base + i
    return uuid.UUID(int=res)
