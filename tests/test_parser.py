from inspect import cleandoc
from unittest import TestCase

from ziggurat import ast
from ziggurat.parser import Parser
from ziggurat.visitor import Display


class ParserTestCases(TestCase):
    maxDiff = None

    def assert_ast(self, actual: ast.AST, expected: str):
        cleaned = cleandoc(expected)
        visitor = Display()
        actual.accept(visitor)

        self.assertEqual(visitor.result, cleaned)

    def test_current(self):
        parser = Parser("abc")

        self.assertEqual(parser.current, "a")
        parser.cursor += 1
        self.assertEqual(parser.current, "b")
        parser.cursor += 1
        self.assertEqual(parser.current, "c")
        parser.cursor += 1
        self.assertEqual(parser.current, None)

        parser = Parser("")
        self.assertEqual(parser.current, None)

    def test_peek(self):
        parser = Parser("abc")
        self.assertEqual(parser.cursor, 0)
        self.assertEqual(parser.current, "a")
        self.assertEqual(parser.peek(), "b")
        self.assertEqual(parser.cursor, 0)
        self.assertEqual(parser.current, "a")

        parser.next()
        parser.next()
        self.assertEqual(parser.cursor, 2)
        self.assertEqual(parser.current, "c")
        self.assertEqual(parser.peek(), None)
        self.assertEqual(parser.cursor, 2)
        self.assertEqual(parser.current, "c")

    def test_next(self):
        parser = Parser("abc")

        self.assertEqual(parser.cursor, 0)
        self.assertEqual(parser.next(), "a")
        self.assertEqual(parser.cursor, 1)
        self.assertEqual(parser.next(), "b")
        self.assertEqual(parser.cursor, 2)
        self.assertEqual(parser.next(), "c")
        self.assertEqual(parser.cursor, 3)
        self.assertEqual(parser.next(), None)
        self.assertEqual(parser.cursor, 4)

    def test_match(self):
        parser = Parser("abc")
        self.assertTrue(parser.match("ab"))
        self.assertEqual(parser.cursor, 2)
        with self.assertRaises(Exception):
            self.assertFalse(parser.match("x"))
        self.assertEqual(parser.cursor, 2)
        self.assertTrue(parser.match("c"))
        self.assertEqual(parser.cursor, 3)

        parser = Parser("  \n\t abc")
        with self.assertRaises(Exception):
            self.assertFalse(parser.match("abc"))
        self.assertEqual(parser.cursor, 0)
        self.assertTrue(parser.match("abc", after_whitespace=True))
        self.assertEqual(parser.cursor, 8)

    def test_peek_match(self):
        parser = Parser("abc")
        self.assertTrue(parser.peek_match("ab"))
        self.assertEqual(parser.cursor, 0)
        self.assertFalse(parser.peek_match("c"))
        self.assertEqual(parser.cursor, 0)
        self.assertTrue(parser.peek_match("abc"))
        self.assertEqual(parser.cursor, 0)

    def test_eat_whitespace(self):
        parser = Parser(" \n\t abc")
        parser.eat_whitespace()
        self.assertEqual(parser.cursor, 4)
        self.assertEqual(parser.current, "a")

    def test_maybe_eat_newline(self):
        parser = Parser("\na")
        parser.maybe_eat_newline()
        self.assertEqual(parser.current, "a")
        parser.maybe_eat_newline()
        self.assertEqual(parser.current, "a")

    def test_word(self):
        parser = Parser("abc xyz")
        self.assertEqual(parser.word(), "abc")
        self.assertEqual(parser.current, " ")
        parser.next()
        self.assertEqual(parser.word(), "xyz")

    def test_text(self):
        text = Parser("abc xyz").text()
        self.assert_ast(text, "Text('abc xyz')")

        text = Parser("abc {xyz}").text()
        self.assert_ast(text, "Text('abc ')")

        text = Parser("abc @if foo@xyz@endif@").text()
        self.assert_ast(text, "Text('abc ')")

        text = Parser("abc \@if foo\@\{xyz\}\@endif\@").text()
        self.assert_ast(text, "Text('abc @if foo@{xyz}@endif@')")

    def test_lookup(self):
        lookup = Parser("{var}").lookup()
        self.assert_ast(lookup, "Lookup(var)")

        lookup = Parser("{ \t\tvar \n\t }").lookup()
        self.assert_ast(lookup, "Lookup(var)")

        lookup = Parser("{obj.attr}").lookup()
        self.assert_ast(lookup, "Lookup(obj.attr)")

        lookup = Parser("{var|upper}").lookup()
        self.assert_ast(lookup, "Lookup(var filter=upper)")

    def test_include(self):
        include = Parser('@include foo.txt@').include()
        expected_ast = "Include(foo.txt)"
        self.assert_ast(include, expected_ast)

    def test_for_loop(self):
        for_loop = Parser("@for i in numbers@i={i}@endfor@").for_loop()
        expected_ast = """
        For(
          name=i
          iterator=numbers
          Block([
            Text('i=')
            Lookup(i)
          ])
        )
        """
        self.assert_ast(for_loop, expected_ast)

    def test_if_stmt(self):
        if_stmt = Parser("@if x@x={x}@endif@").if_stmt()
        expected_ast = """
        If(
          condition=x
          Block([
            Text('x=')
            Lookup(x)
          ])
          Block([
          ])
        )
        """
        self.assert_ast(if_stmt, expected_ast)

        if_stmt = Parser("@if x@x={x}@else@{y}@endif@").if_stmt()
        expected_ast = """
        If(
          condition=x
          Block([
            Text('x=')
            Lookup(x)
          ])
          Block([
            Lookup(y)
          ])
        )
        """
        self.assert_ast(if_stmt, expected_ast)

    def test_block(self):
        ast = Parser(
            cleandoc(
                """
            Hello World!

            @if name@
            Welcome {name}!
            @else@
            Welcome!
            @endif@

            @for i in numbers@
            i = {i}
            @endfor@
        """
            )
        ).parse()

        expected_ast = """
        Block([
          Text('Hello World!\\n\\n')
          If(
            condition=name
            Block([
              Text('Welcome ')
              Lookup(name)
              Text('!\\n')
            ])
            Block([
              Text('Welcome!\\n')
            ])
          )
          Text('\\n')
          For(
            name=i
            iterator=numbers
            Block([
              Text('i = ')
              Lookup(i)
              Text('\\n')
            ])
          )
        ])
        """

        self.assert_ast(ast, expected_ast)
