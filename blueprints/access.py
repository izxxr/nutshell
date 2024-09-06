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

from quart import Blueprint, abort, redirect, render_template, request
from datetime import datetime, timezone
from common.cache import getcache
from models.link import Link


__all__ = (
    "access",
)


access = Blueprint("access", __name__)


async def get_link(code: str):
    link = await getcache().getch(code)
    if link is None:
        abort(404, "Don't know what are you up to but that link DOES NOT exist!")
    if not link.active:
        abort(503, "This link is currently unavailable.")
    return link

async def register_visit(link: Link):
    link.visit_count += 1
    link.last_visited = datetime.now(tz=timezone.utc)
    await link.save()
    return redirect(link.url)

@access.get("/<code>")
@access.post("/<code>")
async def access_link(code: str):
    link = await get_link(code)

    if request.method != "POST":
        link.raw_visit_count += 1
        await link.save()
        if link.password:
            return await render_template("password.html", code=code)
        else:
            return await register_visit(link)
    else:
        form = await request.form
        if form.get("Password") != link.password:
            return await render_template(f"password.html", code=code, invalid=True)
        else:
            return await register_visit(link)

