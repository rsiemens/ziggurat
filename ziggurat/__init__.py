from ziggurat.parser import Parser
from ziggurat.visitor import Renderer


class Template:
    def __init__(self, source, parser_cls=Parser):
        self.ast = parser_cls(source).parse()

    def render(self, ctx):
        renderer = Renderer(ctx)
        self.ast.accept(renderer)
        return renderer.result
