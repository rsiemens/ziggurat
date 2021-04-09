from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Union

if TYPE_CHECKING:
    from ziggurat.visitor import Visitor


class AST(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor):
        ...


class Block(AST):
    def __init__(self, nodes: List[AST]):
        self.nodes = nodes

    def accept(self, visitor: Visitor):
        visitor.visit_block(self)


class If(AST):
    def __init__(self, condition: str, consequence: Block, alternative: Block):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def accept(self, visitor: Visitor):
        visitor.visit_if(self)


class For(AST):
    def __init__(self, name: str, iterator: str, body: Block):
        self.name = name
        self.iterator = iterator
        self.body = body

    def accept(self, visitor: Visitor):
        visitor.visit_for(self)


class Include(AST):
    def __init__(self, source: str):
        self.source = source

    def accept(self, visitor: Visitor):
        visitor.visit_include(self)


class Macro(AST):
    def __init__(self, name: str, parameters: List[str], body: Block):
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor: Visitor):
        visitor.visit_macro(self)


class Text(AST):
    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor: Visitor):
        visitor.visit_text(self)


class Lookup(AST):
    def __init__(self, name: str, transforms: List[str]):
        self.name = name
        self.transforms = transforms

    def accept(self, visitor: Visitor):
        visitor.visit_lookup(self)


class Call(AST):
    def __init__(self, name: str, arguments: Dict[str, Union[str, Lookup]]):
        self.name = name
        self.arguments = arguments

    def accept(self, visitor: Visitor):
        visitor.visit_call(self)
