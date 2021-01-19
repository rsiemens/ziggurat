from unittest import TestCase

from ziggurat import ast
from ziggurat.parser import Parser
from ziggurat.visitor import Renderer


class RendererTestCases(TestCase):
    def render(self, node: ast.AST, context: dict) -> str:
        renderer = Renderer(context)
        node.accept(renderer)
        return renderer.result

    def test_visit_text(self):
        text = ast.Text("abc")
        result = self.render(text, {})
        self.assertEqual(result, "abc")

    def test_visit_lookup(self):
        lookup = ast.Lookup("foo")
        result = self.render(lookup, {"foo": "bar"})
        self.assertEqual(result, "bar")

    def test_visit_if(self):
        if_stmt = ast.If(
            condition="username",
            consequence=ast.Block(
                [ast.Text("Hello, "), ast.Lookup("username"), ast.Text("!")]
            ),
            alternative=ast.Block([ast.Text("Hello, Guest!")]),
        )
        result = self.render(if_stmt, {"username": "rsiemens"})
        self.assertEqual(result, "Hello, rsiemens!")

        result = self.render(if_stmt, {"username": None})
        self.assertEqual(result, "Hello, Guest!")

    def test_visit_for(self):
        for_loop = ast.For(
            name="item",
            iterator="list",
            body=ast.Block([ast.Text("item="), ast.Lookup("item"), ast.Text("\n")]),
        )
        result = self.render(
            for_loop, {"list": ["Bulbasaur", "Charmander", "Squirtle"]}
        )
        self.assertEqual(result, "item=Bulbasaur\nitem=Charmander\nitem=Squirtle\n")

        result = self.render(for_loop, {"list": []})
        self.assertEqual(result, "")
