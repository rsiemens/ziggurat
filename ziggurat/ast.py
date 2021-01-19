from abc import ABC, abstractmethod
from typing import Any, Iterator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ziggurat.visitor import Visitor


class AST(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor"):
        ...


class Block(AST):
    def __init__(self, nodes: List[AST]):
        self.nodes = nodes

    def accept(self, visitor: "Visitor"):
        visitor.visit_block(self)


class If(AST):
    def __init__(self, condition: str, consequence: Block, alternative: Block):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def accept(self, visitor: "Visitor"):
        visitor.visit_if(self)


class For(AST):
    def __init__(self, name: str, iterator: str, body: Block):
        self.name = name
        self.iterator = iterator
        self.body = body

    def accept(self, visitor: "Visitor"):
        visitor.visit_for(self)


class Text(AST):
    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor: "Visitor"):
        visitor.visit_text(self)


class Lookup(AST):
    def __init__(self, name: str, filter: Optional[str] = None):
        self.name = name
        self.filter = filter

    def accept(self, visitor: "Visitor"):
        visitor.visit_lookup(self)
