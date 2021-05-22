"""Jinja2 Templating for bareASGI"""

from typing import (
    Mapping,
    Optional,
    Any,
    Callable,
    Awaitable,
    Tuple
)

import jinja2
from bareasgi import (
    Application,
    HttpResponse,
    Scope,
    Info,
    RouteMatches,
    Content,
    text_writer
)

HttpRequest = Tuple[Scope, Info, RouteMatches, Content]
HttpTemplateRequestCallback = Callable[
    [Scope, Info, RouteMatches, Content],
    Awaitable[Mapping[str, Any]]
]
HttpDecoratorResponse = Callable[
    [Scope, Info, RouteMatches, Content],
    Awaitable[HttpResponse]
]
HttpTemplateResponse = Callable[
    [HttpTemplateRequestCallback],
    HttpDecoratorResponse
]

INFO_KEY = 'bareasgi_jinja2.Jinja2TemplateProvider'


class TemplateNotFoundError(Exception):
    """Raised when a template is not found"""


class Jinja2TemplateProvider:
    """Jinja2TemplateProvider"""

    def __init__(self, env: jinja2.Environment) -> None:
        """The bareASGI Jinja2 template provider

        Args:
            env (jinja2.Environment): The jinja2 environment
        """
        self.env = env

    async def render_string(
            self,
            template_name: str,
            variables: Mapping[str, Any]
    ) -> str:
        """render a string from a template and variables.

        Args:
            template_name (str): The name of the template
            variables (Mapping[str, Any]): The variables to use

        Raises:
            TemplateNotFoundError: When the template was not found

        Returns:
            str: The renderable string
        """
        try:
            jinja2_template: jinja2.Template = self.env.get_template(
                template_name
            )
        except jinja2.TemplateNotFound as error:
            raise TemplateNotFoundError(
                f"Template '{template_name}' not found"
            ) from error

        if self.env.enable_async:  # type: ignore
            return await jinja2_template.render_async(**variables)
        else:
            return jinja2_template.render_async(**variables)  # type: ignore

    async def __call__(
            self,
            status: int,
            template_name: str,
            variables: Mapping[str, Any],
            encoding: str = 'utf-8'
    ) -> HttpResponse:
        try:
            text = await self.render_string(template_name, variables)
            content_type = f'text/html; chartset={encoding}'
            headers = [
                (b'content-type', content_type.encode())
            ]
            return status, headers, text_writer(text)
        except TemplateNotFoundError as error:
            headers = [
                (b'content-type', b'text/plain')
            ]
            return 500, headers, text_writer(str(error), encoding=encoding)


def template(
        template_name: str,
        status: int = 200,
        encoding: str = 'utf-8',
        info_key: Optional[str] = None
) -> HttpTemplateResponse:
    """Registers a jinja2 template callback.

    For example:

    ```python
    @template('example1.html')
    async def http_request_handler(scope, info, matches, content):
        return {'name': 'rob'}
    ```

    Args:
        template_name (str): The name of the template.
        status (int, optional): The OK status. Defaults to 200.
        encoding (str, optional): The encdoing used for generating the body.. Defaults to 'utf-8'.
        info_key (Optional[str], optional): An optional key to overide the key
            in the supplied info dict where the jinja2 Environment is held.
            Defaults to None.

    Returns:
        HttpTemplateResponse: The decorated function
    """

    def decorator(func: HttpTemplateRequestCallback) -> HttpDecoratorResponse:
        async def wrapper(*args) -> HttpResponse:
            # Index from end as class methods will have an extra 'self' parameter.
            info = args[-3]
            provider: Jinja2TemplateProvider = info[info_key or INFO_KEY]
            variables = await func(*args)
            return await provider(status, template_name, variables, encoding)

        return wrapper

    return decorator


def add_jinja2(app: Application, env: jinja2.Environment, info_key: Optional[str] = None) -> None:
    """Adds jinja2 support ro bareASGI.

    This helper function can be used as follows:

    ```python
    app = Application()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('/path/to/templates')),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )

    add_jinja2(app, env)
    ```

    Args:
        app (Application): The bareASGI Application.
        env (jinja2.Environment): The jinja2 Environment
        info_key (Optional[str], optional): An optional key to overide the key
            in the supplied info dict where the jinja2 Environment is held.
            Defaults to None.
    """
    app.info[info_key or INFO_KEY] = Jinja2TemplateProvider(env)
