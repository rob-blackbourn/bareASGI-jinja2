from typing import Mapping, Any
import jinja2
import os.path
import uvicorn
from bareasgi import (
    Scope,
    Info,
    RouteMatches,
    Content,
    Application
)
from bareasgi_jinja2 import add_jinja2, template

here = os.path.abspath(os.path.dirname(__file__))


@template('example1.html')
async def http_request_handler(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> Mapping[str, Any]:
    return {'name': 'rob'}


app = Application()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(here, 'templates')),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    enable_async=True
)

add_jinja2(app, env)

app.http_router.add({'GET'}, '/example1', http_request_handler)

uvicorn.run(app, port=9010)
