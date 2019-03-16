# bareASGI-jinja2

Jinja2 support for [bareASGI](http://github.com/rob-blackbourn/bareasgi) (read the [documentation](https://bareasgi-jinja2.readthedocs.io/en/latest/))

## Usage

Try the following.

```python
from typing import Mapping, Any
import jinja2
import os.path
import uvicorn
from bareasgi import Application
import bareasgi_jinja2

here = os.path.abspath(os.path.dirname(__file__))

@bareasgi_jinja2.template('example1.html')
async def http_request_handler(scope, info, matches, content):
    return {'name': 'rob'}

app = Application()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(here, 'templates')),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    enable_async=True
)

bareasgi_jinja2.add_jinja2(app, env)

app.http_router.add({'GET'}, '/example1', http_request_handler)

uvicorn.run(app, port=9010)

```
