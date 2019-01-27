from typing import Mapping, Optional, Any, Callable, Awaitable, Tuple
import jinja2
from bareasgi import (
    Application,
    HttpResponse,
    text_writer,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpRequestCallback
)

INFO_KEY = 'bareasgi_jinja2'


class Jinja2TemplateProvider:

    def __init__(self, env: jinja2.Environment) -> None:
        self.env = env

    def render_string(self, template_name: str, variables: Mapping[str, Any]) -> str:
        # Get the template.
        try:
            template: jinja2.Template = self.env.get_template(template_name)
        except jinja2.TemplateNotFound as e:
            raise RuntimeError(f"Template '{template_name}' not found")
        except Exception as error:
            print(error)
            raise

        text = template.render(**variables)

        return text

    async def __call__(
            self,
            status: int,
            template_name: str,
            variables: Mapping[str, Any],
            encoding: str = 'utf-8'
    ) -> HttpResponse:
        try:
            text = self.render_string(template_name, variables)
            content_type = f'text/html; chartset={encoding}'
            return status, [(b'content-type', content_type.encode())], text_writer(text)
        except RuntimeError as error:
            return 500, [(b'content-type', b'text/plain')], text_writer(str(error))


HttpRequest = Tuple[Scope, Info, RouteMatches, Content]
HttpTemplateRequestCallback = Callable[[Scope, Info, RouteMatches, Content], Awaitable[Mapping[str, Any]]]
HttpDecoratorResponse = Callable[[Scope, Info, RouteMatches, Content], Awaitable[HttpResponse]]
HttpTemplateResponse = Callable[[HttpTemplateRequestCallback], HttpDecoratorResponse]


def template(
        template_name: str,
        status: int = 200,
        encoding: str = 'utf-8',
        info_key: Optional[str] = None
) -> HttpTemplateResponse:
    def decorator(func: HttpTemplateRequestCallback) -> HttpDecoratorResponse:
        async def wrapper(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
            provider: Jinja2TemplateProvider = info[info_key or INFO_KEY]
            variables = await func(scope, info, matches, content)
            return await provider(status, template_name, variables, encoding)

        return wrapper

    return decorator


def add_jinja2(app: Application, env: jinja2.Environment, info_key: Optional[str] = None) -> None:
    app.info[info_key or INFO_KEY] = Jinja2TemplateProvider(env)
