# bareASGI-jinja2

Jinja2 support for [bareASGI](http://github.com/rob-blackbourn/bareasgi)
(read the [documentation](https://rob-blackbourn.github.io/bareASGI-jinja2/))

## Usage

Try the following.

```python
from typing import Mapping, Any
import jinja2
import os.path
import uvicorn
from bareasgi import Application
from bareasgi_jinja2 import Jinja2TemplateProvider, add_jinja2

here = os.path.abspath(os.path.dirname(__file__))

async def http_request_handler(request: HttpRequest) -> HttpResponse:
    """Handle the request"""
    template = 'example1.html'
    variables = {'name': 'rob'}
    return await Jinja2TemplateProvider.apply(request, template, variables)

app = Application()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(here, 'templates')),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    enable_async=True
)

add_jinja2(app, env)

app.http_router.add({'GET'}, '/example1', http_request_handler)

uvicorn.run(app, port=9010)

```
