"""Jinja2 Templating for bareASGI"""

from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    Optional
)

import jinja2
from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

HttpTemplateRequestCallback = Callable[
    [HttpRequest],
    Awaitable[Mapping[str, Any]]
]

INFO_KEY = '__bareasgi_jinja2.Jinja2TemplateProvider__'


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

        if self.env.is_async:  # type: ignore
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
            content_type = f'text/html; charset={encoding}'
            headers = [
                (b'content-type', content_type.encode())
            ]
            return HttpResponse(status, headers, text_writer(text))
        except TemplateNotFoundError as error:
            headers = [
                (b'content-type', b'text/plain')
            ]
            return HttpResponse(
                500,
                headers,
                text_writer(str(error), encoding=encoding)
            )

    @classmethod
    async def apply(
            cls,
            request: HttpRequest,
            template_name: str,
            variables: Mapping[str, Any],
            *,
            status: int = 200,
            encoding: str = 'utf-8',
            info_key: str = INFO_KEY
    ) -> HttpResponse:
        provider: Jinja2TemplateProvider = request.info[info_key]
        return await provider(status, template_name, variables, encoding)


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
        info_key (Optional[str], optional): An optional key to override the key
            in the supplied info dict where the jinja2 Environment is held.
            Defaults to None.
    """
    app.info[info_key or INFO_KEY] = Jinja2TemplateProvider(env)
