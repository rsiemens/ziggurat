from pathlib import Path
from typing import Optional
from unittest import TestCase

from ziggurat import Template, ast
from ziggurat.visitor import Renderer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class RendererTestCases(TestCase):
    def render(
        self, node: ast.AST, context: dict, base: Optional[Path] = None
    ) -> Renderer:
        renderer = Renderer(context, Template.transforms, base=base)
        node.accept(renderer)
        return renderer

    def test_visit_text(self):
        text = ast.Text("abc")
        renderer = self.render(text, {})
        self.assertEqual(renderer.result, "abc")

    def test_visit_lookup(self):
        lookup = ast.Lookup("foo", transforms=[])
        renderer = self.render(lookup, {"foo": "bar"})
        self.assertEqual(renderer.result, "bar")

        renderer = self.render(lookup, {"foo": 42})
        self.assertEqual(renderer.result, "42")

        lookup = ast.Lookup("foo.bar", transforms=[])
        renderer = self.render(lookup, {"foo": {"bar": "baz"}})
        self.assertEqual(renderer.result, "baz")

        lookup = ast.Lookup("foo.bar", transforms=[])
        Foo = type("Foo", (), {"bar": 42})
        renderer = self.render(lookup, {"foo": Foo()})
        self.assertEqual(renderer.result, "42")

        lookup = ast.Lookup("foo", transforms=["upper"])
        renderer = self.render(lookup, {"foo": "bar"})
        self.assertEqual(renderer.result, "BAR")

        lookup = ast.Lookup("foo", transforms=["upper", "lower"])
        renderer = self.render(lookup, {"foo": "BaR"})
        self.assertEqual(renderer.result, "bar")

    def test_visit_if(self):
        if_stmt = ast.If(
            condition="username",
            consequence=ast.Block(
                [
                    ast.Text("Hello, "),
                    ast.Lookup("username", transforms=[]),
                    ast.Text("!"),
                ]
            ),
            alternative=ast.Block([ast.Text("Hello, Guest!")]),
        )
        renderer = self.render(if_stmt, {"username": "rsiemens"})
        self.assertEqual(renderer.result, "Hello, rsiemens!")

        renderer = self.render(if_stmt, {"username": None})
        self.assertEqual(renderer.result, "Hello, Guest!")

    def test_visit_for(self):
        for_loop = ast.For(
            name="item",
            iterator="list",
            body=ast.Block(
                [ast.Text("item="), ast.Lookup("item", transforms=[]), ast.Text("\n")]
            ),
        )
        renderer = self.render(
            for_loop, {"list": ["Bulbasaur", "Charmander", "Squirtle"]}
        )
        self.assertEqual(
            renderer.result, "item=Bulbasaur\nitem=Charmander\nitem=Squirtle\n"
        )

        renderer = self.render(for_loop, {"list": []})
        self.assertEqual(renderer.result, "")

    def test_visit_include(self):
        include = ast.Include(f'{FIXTURES_DIR / "base.txt"}')
        renderer = self.render(include, {"foo": "bar"}, base=FIXTURES_DIR)

        self.assertEqual(renderer.result, "Some base with foo=bar\n")
        # TODO: test include cache

    def test_visit_macro(self):
        body = ast.Block(
            [
                ast.Text('<input type="'),
                ast.Lookup("type", transforms=[]),
                ast.Text('" value="'),
                ast.Lookup("value", transforms=[]),
                ast.Text('">'),
            ]
        )
        macro = ast.Macro(name="input", parameters=["type", "value"], body=body)
        renderer = self.render(macro, {})
        self.assertEqual(renderer.result, "")
        self.assertEqual(renderer.macros, {"input": (["type", "value"], body)})

    def test_visit_call_macro(self):
        call = ast.Call(name="foo", arguments={})
        renderer = Renderer(context={}, transforms={})
        renderer.macros["foo"] = ([], ast.Text("foo text"))
        call.accept(renderer)
        self.assertEqual(renderer.result, "foo text")

        body = ast.Block(
            [
                ast.Text('<input type="'),
                ast.Lookup("type", transforms=[]),
                ast.Text('" value="'),
                ast.Lookup("value", transforms=[]),
                ast.Text('">'),
            ]
        )
        call = ast.Call(
            name="input",
            arguments={"type": "text", "value": ast.Lookup("val", transforms=[])},
        )
        renderer = Renderer(context={"val": "hi"}, transforms={})
        renderer.macros["input"] = (["type", "value"], body)
        call.accept(renderer)
        self.assertEqual(renderer.result, '<input type="text" value="hi">')
