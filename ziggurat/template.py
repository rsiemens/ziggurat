from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type

from ziggurat.parser import Parser
from ziggurat.visitor import Renderer


class Template:
    filters = {"upper": str.upper, "lower": str.lower, "capitalize": str.capitalize}

    def __init__(
        self,
        source: str,
        encoding: str = "utf8",
        parser_cls: Type[Parser] = Parser,
        renderer_cls: Type[Renderer] = Renderer,
    ):
        self.source = Path(source)
        with open(source, "r", encoding=encoding) as tmpl:
            self.renderer_cls = renderer_cls
            self.ast = parser_cls(tmpl.read()).parse()

    def render(self, ctx: Dict[str, Any]) -> str:
        renderer = self.renderer_cls(ctx, self.filters, self.source.parent)
        self.ast.accept(renderer)
        return renderer.result


def register_filter(func: Callable[[str], str], name: Optional[str] = None):
    if name is None:
        name = func.__name__
    Template.filters[name] = func
    return func
