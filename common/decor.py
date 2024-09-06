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

from typing import Any
from quart import request, abort
from functools import wraps

import os
import dotenv

__all__ = (
    "auth_required"
)

dotenv.load_dotenv()

try:
    AUTH_TOKEN = os.environ["NUTSHELL_AUTH_TOKEN"]
except KeyError:
    raise RuntimeError("No authorization token supplied in environment variables.")
else:
    assert len(AUTH_TOKEN) > 10, "NUTSHELL_AUTH_TOKEN must be greater than 10 characters in length."

def auth_required(f):
    """Decorator to ensure authorized access to a route."""
    @wraps(f)
    async def decorated_function(*args: Any, **kwargs: Any):
        auth = request.headers.get("Authorization")
        if not auth:
            return await abort(401, {"error": "This resource requires authorization."})

        scheme, token = auth.strip().split(" ")
        if scheme != "Bearer":
            return await abort(400, {"error": "Unsupported authorization scheme used."})
        if token != AUTH_TOKEN:
            return await abort(403, {"error": "Authorization failed."})

        return await f(*args, **kwargs)

    return decorated_function
