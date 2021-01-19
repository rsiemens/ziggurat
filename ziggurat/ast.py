from abc import ABC, abstractmethod


class AST(ABC):
    @abstractmethod
    def accept(self, visitor):
        ...


class Block(AST):
    def __init__(self, nodes):
        self.nodes = nodes

    def accept(self, visitor):
        return visitor.visit_block(self)


class If(AST):
    def __init__(self, condition, consequence, alternative):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def accept(self, visitor):
        return visitor.visit_if(self)


class For(AST):
    def __init__(self, name, iterator, body):
        self.name = name
        self.iterator = iterator
        self.body = body

    def accept(self, visitor):
        visitor.visit_for(self)


class Text(AST):
    def __init__(self, text):
        self.text = text

    def accept(self, visitor):
        return visitor.visit_text(self)


class Lookup(AST):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_lookup(self)
