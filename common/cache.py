# MIT License

# Copyright (c) 2024 Izhar Ahmad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Optional
from collections import OrderedDict
from quart import current_app
from models.link import Link

__all__ = (
    "LRUCache",
    "getcache",
)


class LRUCache:
    """Links cache implementation based on least-recently-used strategy.

    This implementation uses the simple :class:`collections.OrderedDict`
    to provide access to stored links via their code.

    The maxlen argument determines the amount of links stored in the
    cache. Exceeding this number will cause the least recently accessed
    link to be evicted from cache.
    """

    def __init__(self, maxlen: int) -> None:
        self._cache = OrderedDict()  # order: most recent -> least recent
        self._maxlen = maxlen

    def add_link(self, link: Link) -> None:
        """Adds a link to the start of cache.

        If max length is reached, the least recently used
        link i.e. the one in the last of internal dictionary
        will be evicted.
        """
        if len(self._cache) == self._maxlen:
            self._cache.popitem()

        self._cache[link.code] = link
        self._cache.move_to_end(link.code, last=False)

    def get_link(self, code: str, silent: bool = False) -> Optional[Link]:
        """Get a cached link from its code.

        The accessed link is moved to the start of the cache
        unless silent is True, in which case the target link
        is returned silently.
        """
        try:
            link = self._cache[code]
        except KeyError:
            return None
        else:
            # It might be possible to consider "incremental moving" strategy here
            # for moving the link. That is, the accessed link will move one position
            # ahead upon access instead of moving to the start each time. This is more
            # complex to implement.
            self._cache.move_to_end(code, last=False)
            return link

    def delete_link(self, code: str) -> Optional[Link]:
        """Removes a link from the cache."""
        return self._cache.pop(code, None)

    async def getch(self, code: str, silent: bool = False) -> Optional[Link]:
        """A syntatic sugar method to get-or-fetch a link.

        This method first checks the cache for the link and if
        not found, fetches it from the database.

        The fetched link is cached and returned upon subsequent
        accesses. If None is returned, the link code is invalid.
        """
        link = self.get_link(code, silent=silent)
        if link is None:
            link = await Link.get_or_none(code=code)
        if link is not None:
            self.add_link(link)
        return link

def getcache() -> LRUCache:
    """Returns the global cache instance."""
    return current_app.config["LINKS_CACHE"]
