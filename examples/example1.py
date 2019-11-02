"""An example of jinja2 templating"""

import os.path
from typing import Mapping, Any

import jinja2
import uvicorn
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content
)

import bareasgi_jinja2

HERE = os.path.abspath(os.path.dirname(__file__))


@bareasgi_jinja2.template('example1.html')
async def http_request_handler(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> Mapping[str, Any]:
    """Handle the request"""
    return {'name': 'rob'}


app = Application()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(HERE, 'templates')),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    enable_async=True
)

bareasgi_jinja2.add_jinja2(app, env)

app.http_router.add({'GET'}, '/example1', http_request_handler)

uvicorn.run(app, port=9010)
