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
from tortoise import Model, fields
from pydantic import BaseModel, Field, HttpUrl, AwareDatetime

import string
import random
import datetime

__all__ = (
    "Link",
    "LinkSchema",
    "generate_code",
)


CHARACTERS = string.ascii_letters + string.digits
SIZE = 6

def generate_code():
    return "".join(random.sample(CHARACTERS, SIZE))


class Link(Model):
    """Represents a shortened link stored in the database."""

    code = fields.CharField(max_length=100, primary_key=True, default=generate_code)
    """The unique shortened code."""

    url = fields.TextField()
    """The URL that the link redirects to."""

    password = fields.TextField(null=True, default=None)
    """The password required to access this link, if any."""

    created_at = fields.DatetimeField(auto_now_add=True)
    """The time when this link was created."""

    active = fields.BooleanField(default=True)
    """Whether this link is currently active."""

    raw_visit_count = fields.BigIntField(default=0)
    """Number of times the link was visited."""

    visit_count = fields.BigIntField(default=0)
    """Number of times the link was visited successfully."""

    last_visited = fields.DatetimeField(auto_now_add=True)
    """The last time this link was visited."""

    def pd_schema(self):
        return LinkSchema(
            code=self.code,
            url=self.url,
            password=self.password,
            created_at=self.created_at,
            active=self.active,
            visit_count=self.visit_count,
            raw_visit_count=self.raw_visit_count,
            last_visited=self.last_visited,
        )


class LinkSchema(BaseModel):
    """The Pydantic model for link object."""

    code: str = Field(default_factory=generate_code, min_length=2, max_length=100)
    url: HttpUrl
    password: Optional[str] = None
    created_at: Optional[AwareDatetime] = None  # late binding
    active: bool = True
    visit_count: int = 0
    raw_visit_count: int = 0
    last_visited: AwareDatetime = Field(default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc))
