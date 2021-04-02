import string
from typing import List, Optional

from ziggurat import ast


class Parser:
    def __init__(self, source: str):
        self.source = source
        self.cursor = 0

    @property
    def current(self) -> Optional[str]:
        try:
            return self.source[self.cursor]
        except IndexError:
            return None

    def peek(self) -> Optional[str]:
        try:
            return self.source[self.cursor + 1]
        except IndexError:
            return None

    def next(self) -> Optional[str]:
        self.cursor += 1
        try:
            return self.source[self.cursor - 1]
        except IndexError:
            return None

    def match(self, tokens: str, after_whitespace: bool = False) -> bool:
        matched = ""
        if after_whitespace:
            self.eat_whitespace()

        for token in tokens:
            if self.current is not None and self.current == token:
                matched += self.current
                self.next()
            else:
                raise Exception(f"Expected {tokens}, but got {repr(matched)} instead")
        return True

    def peek_match(self, tokens: str) -> bool:
        save_point = self.cursor
        for token in tokens:
            if token == self.source[self.cursor]:
                self.cursor += 1
            else:
                self.cursor = save_point
                return False
        self.cursor = save_point
        return True

    def eat_whitespace(self):
        while self.current in string.whitespace:
            self.next()

    def maybe_eat_newline(self):
        if self.current == "\n":
            self.next()

    def word(self) -> str:
        result = ""
        following_chars = string.ascii_letters + string.digits + "_./"

        if self.current and self.current in string.ascii_letters:
            result += self.next()  # type: ignore

        while self.current and self.current in following_chars:
            result += self.next()  # type: ignore
        return result

    def block(self) -> ast.Block:
        nodes: List[ast.AST] = []
        while self.current:
            if self.peek_match("@if "):
                nodes.append(self.if_stmt())
            elif self.peek_match("@for "):
                nodes.append(self.for_loop())
            elif self.peek_match("@include "):
                nodes.append(self.include())
            elif self.current == "{":
                nodes.append(self.lookup())
            elif self.current != "@":
                nodes.append(self.text())
            else:
                break
        return ast.Block(nodes)

    def if_stmt(self) -> ast.If:
        """
        @if thing@
           {thing}
        @else@
            Nothing
        @endif@
        """
        self.match("@if ")
        word = self.word()
        self.match("@", after_whitespace=True)
        self.maybe_eat_newline()

        consequence = self.block()
        alternative = ast.Block([])

        if self.peek_match("@else@"):
            self.match("@else@")
            self.maybe_eat_newline()
            alternative = self.block()

        self.match("@endif@")
        self.maybe_eat_newline()

        return ast.If(word, consequence, alternative)

    def for_loop(self) -> ast.For:
        """
        @for item in items@
            {item}
        @endfor@
        """
        self.match("@for ")
        word = self.word()

        self.match("in", after_whitespace=True)
        self.eat_whitespace()
        iterator = self.word()

        self.match("@", after_whitespace=True)
        self.maybe_eat_newline()

        body = self.block()
        self.match("@endfor@")
        self.maybe_eat_newline()

        return ast.For(word, iterator, body)

    def include(self) -> ast.Include:
        self.match("@include ")
        word = self.word()
        self.match("@", after_whitespace=True)
        return ast.Include(word)

    def lookup(self) -> ast.Lookup:
        """
        {variable | optional_filter}
        """
        self.match("{")
        self.eat_whitespace()
        word = self.word()
        self.eat_whitespace()

        filter = None
        if self.current == "|":
            self.next()
            self.eat_whitespace()
            filter = self.word()
            self.eat_whitespace()

        self.match("}")

        return ast.Lookup(word, filter)

    def text(self) -> ast.Text:
        result = ""
        while self.current:
            if self.current in [None, "@", "{"]:
                break
            elif self.current == "\\" and self.peek() in ["@", "{", "}"]:
                self.next()  # skip "\"
            result += self.next()  # type: ignore

        return ast.Text(result)

    def parse(self) -> ast.Block:
        return self.block()
