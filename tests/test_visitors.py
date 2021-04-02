from pathlib import Path
from typing import Optional
from unittest import TestCase

from ziggurat import Template, ast
from ziggurat.visitor import Renderer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class RendererTestCases(TestCase):
    def render(self, node: ast.AST, context: dict, base: Optional[Path] = None) -> str:
        renderer = Renderer(context, Template.transforms, base=base)
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

        result = self.render(lookup, {"foo": 42})
        self.assertEqual(result, "42")

        lookup = ast.Lookup("foo.bar")
        result = self.render(lookup, {"foo": {"bar": "baz"}})
        self.assertEqual(result, "baz")

        lookup = ast.Lookup("foo.bar")
        Foo = type("Foo", (), {"bar": 42})
        result = self.render(lookup, {"foo": Foo()})
        self.assertEqual(result, "42")

        lookup = ast.Lookup("foo", transform="upper")
        result = self.render(lookup, {"foo": "bar"})
        self.assertEqual(result, "BAR")

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

    def test_visit_include(self):
        include = ast.Include(f'{FIXTURES_DIR / "base.txt"}')
        result = self.render(include, {"foo": "bar"}, base=FIXTURES_DIR)

        self.assertEqual(result, "Some base with foo=bar\n")
