import string
from ziggurat import ast


class Parser:
    """
    Grammar
    =======

    TEMPLATE := TEXT | TEXT_LOOKUP | CONTROL_FLOW
    CONTROL_FLOW := IF | LOOP
    IF := "@if" " "+ LOOKUP " "* "@" TEMPLATE "@endif@"
    TEXT_LOOKUP := "{" LOOKUP "}"
    LOOKUP := a-zA-Z a-zA-Z0-9_*
    """

    def __init__(self, source):
        self.source = source
        self.cursor = 0

    @property
    def current(self):
        try:
            return self.source[self.cursor]
        except IndexError:
            return None

    def next(self):
        self.cursor += 1
        try:
            return self.source[self.cursor - 1]
        except IndexError:
            return None

    def match(self, tokens, after_whitespace=False):
        matched = ""

        if after_whitespace:
            self.eat_whitespace()

        for token in tokens:
            matched += self.current

            if self.current == token:
                self.next()
            else:
                raise Exception(f"Expected {tokens}, but got {repr(matched)} instead")
        return matched

    def peek_match(self, tokens):
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

    def word(self):
        result = ""
        while self.current and self.current in string.ascii_letters:
            result += self.next()
        return result

    def block(self):
        nodes = []
        while self.current:
            if self.peek_match("@if "):
                nodes.append(self.if_stmt())
            if self.peek_match("@for "):
                nodes.append(self.for_loop())
            elif self.current == "{":
                nodes.append(self.lookup())
            elif self.current != "@":
                nodes.append(self.text())
            else:
                break
        return ast.Block(nodes)

    def if_stmt(self):
        """
        @if thing@
           {thing} 
        @else@
            Nothing there
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

    def for_loop(self):
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

        self.eat_whitespace()
        self.match("@")
        self.maybe_eat_newline()

        body = self.block()
        self.match("@endfor@")
        self.maybe_eat_newline()

        return ast.For(word, iterator, body)

    def lookup(self):
        """
        {variable}
        """
        self.match("{")
        self.eat_whitespace()
        word = self.word()
        self.eat_whitespace()
        self.match("}")

        return ast.Lookup(word)

    def text(self):
        result = ""
        while self.current not in [None, "@", "{"]:
            result += self.next()

        return ast.Text(result)

    def parse(self):
        return self.block()
