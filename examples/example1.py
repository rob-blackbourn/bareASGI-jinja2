"""An example of jinja2 templating"""

from typing import Mapping, Any

import jinja2
import pkg_resources
import uvicorn
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content
)

import bareasgi_jinja2


@bareasgi_jinja2.template('example1.html')
async def http_request_handler(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> Mapping[str, Any]:
    """Handle the request"""
    return {'name': 'rob'}


@bareasgi_jinja2.template('notemplate.html')
async def handle_no_template(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> Mapping[str, Any]:
    """This is what happens if there is no template"""
    return {'name': 'rob'}

if __name__ == '__main__':

    TEMPLATES = pkg_resources.resource_filename(__name__, "templates")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )

    app = Application()
    bareasgi_jinja2.add_jinja2(app, env)

    app.http_router.add({'GET'}, '/example1', http_request_handler)
    app.http_router.add({'GET'}, '/notemplate', handle_no_template)

    uvicorn.run(app, port=9010)
