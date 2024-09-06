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

from quart import Blueprint, Response, request
from pydantic import ValidationError
from common.decor import auth_required
from common.cache import getcache
from models.link import LinkSchema, Link

__all__ = (
    "links",
)


links = Blueprint("links", __name__, url_prefix="/links")

@links.post("/")
@auth_required
async def create_link():
    data = await request.get_json() or {}
    try:
        link = LinkSchema(**data)
    except ValidationError as err:
        return err.errors(include_input=False), 400

    cache = getcache()
    link = await cache.get_link(link.code)

    if link is not None:
        return {"error": "Code is taken."}, 409

    db_link = await Link.create(
        code=link.code,
        url=link.url,
        password=link.password,
        active=link.active,
    )
    link.created_at = db_link.created_at
    link.last_visited = db_link.last_visited
    return link.model_dump(mode="json")


@links.get("/<code>")
@auth_required
async def get_link(code: str):
    link = await getcache().getch(code)
    if link is None:
        return {"error": "Link not found."}, 404

    return link.pd_schema().model_dump(mode="json")


@links.get("/")
@auth_required
async def get_all_links():
    links = await Link.all()
    return [l.pd_schema().model_dump(mode="json") for l in links]

@links.delete("/<code>")
@auth_required
async def delete_link(code: str):
    cache = getcache()
    link = await cache.getch(code)
    if link is None:
        return {"error": "Link not found."}, 404

    cache.delete_link(code)
    await link.delete()
    return Response(None), 204


@links.patch("/<code>")
@auth_required
async def update_link(code: str):
    link = await getcache().getch(code)
    if link is None:
        return {"error": "Link not found."}, 404

    data = await request.get_json() or {}
    
    # fields that cannot be updated
    data.pop("code", None)
    data.pop("created_at", None)
    data.pop("visit_count", None)
    data.pop("last_visited", None)

    link.update_from_dict(data)
    await link.save()

    return link.pd_schema().model_dump(mode="json")
