import hashlib
import string
from functools import cache

from shared import str_increment


@cache
def md5_hash(s: str):
    return hashlib.md5(s.encode()).hexdigest()


def brute_force(
    start: str, stop: str, digest: str, charset: str = string.ascii_lowercase
):
    while start != str_increment(stop, charset):
        if md5_hash(start) == digest:
            return start
        start = str_increment(start, charset)
    return None
