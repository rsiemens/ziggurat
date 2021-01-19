from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING

from ziggurat import ast


class Visitor(ABC):
    def visit_block(self, node: ast.Block):
        ...

    def visit_if(self, node: ast.If):
        ...

    def visit_for(self, node: ast.For):
        ...

    def visit_text(self, node: ast.Text):
        ...

    def visit_lookup(self, node: ast.Lookup):
        ...


class Renderer(Visitor):
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.result = ""

    def visit_block(self, node: ast.Block):
        for child_node in node.nodes:
            child_node.accept(self)

    def visit_if(self, node: ast.If):
        if self.context[node.condition]:
            node.consequence.accept(self)
        else:
            node.alternative.accept(self)

    def visit_for(self, node: ast.For):
        iterator = self.context[node.iterator]
        previous = self.context.get(node.name)

        for i in iterator:
            self.context[node.name] = i
            node.body.accept(self)

        if previous:
            self.context[node.name] = previous
        elif node.name in self.context:
            del self.context[node.name]

    def visit_text(self, node: ast.Text):
        self.result += node.text

    def visit_lookup(self, node: ast.Lookup):
        value = self.context[node.name]
        if not isinstance(value, str):
            value = str(value)
        self.result += value


class Display(Visitor):
    def __init__(self):
        self.depth = 0
        self._result = ""

    @property
    def result(self) -> str:
        return self._result.strip()

    def depth_log(self, txt: str):
        self._result += f'{"  " * self.depth}{txt}\n'

    def visit_block(self, node: ast.Block):
        self.depth_log("Block([")
        self.depth += 1
        for child_node in node.nodes:
            child_node.accept(self)
        self.depth -= 1
        self.depth_log("])")

    def visit_if(self, node: ast.If):
        self.depth_log("If(")
        self.depth += 1
        self.depth_log(f"condition={node.condition}")
        node.consequence.accept(self)
        node.alternative.accept(self)
        self.depth -= 1
        self.depth_log(")")

    def visit_for(self, node: ast.For):
        self.depth_log("For(")
        self.depth += 1
        self.depth_log(f"name={node.name}")
        self.depth_log(f"iterator={node.iterator}")
        node.body.accept(self)
        self.depth -= 1
        self.depth_log(")")

    def visit_lookup(self, node: ast.Lookup):
        self.depth_log(f"Lookup({node.name})")

    def visit_text(self, node: ast.Text):
        self.depth_log(f"Text({repr(node.text)})")
