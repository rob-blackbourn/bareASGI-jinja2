from typing import Mapping, Any
from jinja2 import FileSystemLoader, select_autoescape, Environment
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
async def foo(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> Mapping[str, Any]:
    return {'name': 'rob'}


app = Application()

env = Environment(
    loader=FileSystemLoader(os.path.join(here, 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

add_jinja2(
    app,
    env
)

app.http_router.add({'GET'}, '/example1', foo)

uvicorn.run(app, port=9010)
