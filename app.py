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

from quart import Quart, redirect
from tortoise import Tortoise
from os import environ
from common.cache import LRUCache
from blueprints.links import links
from blueprints.access import access

__all__ = (
    "app",
)


app = Quart("__name__")
app.config["TORTOISE_SETUP_DONE"] = False
app.config["LINKS_CACHE"] = LRUCache(maxlen=int(environ.get("NUTSHELL_CACHE_LIMIT", 50)))
app.register_blueprint(links)
app.register_blueprint(access)


@app.get("/")
async def index():
    return redirect("https://github.com/izxxr")


@app.before_request
async def before_request_hook():
    if not app.config.get("TORTOISE_SETUP_DONE", True):
        print("[DATABASE] Generating database schema")

        await Tortoise.init(
            db_url='sqlite://db.sqlite3',
            modules={'models': ['models']}
        )
        await Tortoise.generate_schemas()

        app.config["TORTOISE_SETUP_DONE"] = True

if __name__ == "__main__":
    app.run()
