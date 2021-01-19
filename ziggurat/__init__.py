from typing import Any, Dict, Type

from ziggurat.parser import Parser
from ziggurat.visitor import Renderer


class Template:
    filters = {"upper": str.upper, "lower": str.lower, "capitalize": str.capitalize}

    def __init__(self, source: str, parser_cls: Type[Parser] = Parser):
        self.ast = parser_cls(source).parse()

    def render(self, ctx: Dict[str, Any]) -> str:
        renderer = Renderer(ctx, self.filters)
        self.ast.accept(renderer)
        return renderer.result
