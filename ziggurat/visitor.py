from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ziggurat import ast


class Visitor(ABC):
    @abstractmethod
    def visit_block(self, node: ast.Block):
        ...

    @abstractmethod
    def visit_if(self, node: ast.If):
        ...

    @abstractmethod
    def visit_for(self, node: ast.For):
        ...

    @abstractmethod
    def visit_text(self, node: ast.Text):
        ...

    @abstractmethod
    def visit_lookup(self, node: ast.Lookup):
        ...

    @abstractmethod
    def visit_include(self, node: ast.Include):
        ...

    @abstractmethod
    def visit_macro(self, node: ast.Macro):
        ...


MacroDict = Dict[str, Tuple[List[str], ast.Block]]


class Renderer(Visitor):
    def __init__(
        self,
        context: Dict[str, Any],
        transforms: Dict[str, Callable],
        base: Optional[Path] = None,
    ):
        self.context = context
        self.transforms = transforms
        self.base = base
        self.include_cache: Dict[str, str] = {}
        self.macros: MacroDict = {}
        self.result = ""

    def visit_block(self, node: ast.Block):
        for child_node in node.nodes:
            child_node.accept(self)

    def visit_if(self, node: ast.If):
        parts = node.condition.split(".")

        if len(parts) == 1:
            value = self.context[node.condition]
        else:
            ctx = self.context
            for part in parts:
                if isinstance(ctx, dict):
                    ctx = ctx[part]
                else:
                    ctx = getattr(ctx, part)
            value = ctx

        if value:
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

    def visit_include(self, node: ast.Include):
        from ziggurat.template import Template

        cached_result = self.include_cache.get(node.source)
        if cached_result:
            self.result += cached_result
            return

        if self.base is None:
            raise ValueError("You must provide a base path when using @include file@")
        template = Template(str(self.base / node.source))
        result = template.render(self.context)
        self.include_cache[node.source] = result
        self.result += result

    def visit_macro(self, node: ast.Macro):
        self.macros[node.name] = (node.parameters, node.body)

    def visit_text(self, node: ast.Text):
        self.result += node.text

    def visit_lookup(self, node: ast.Lookup):
        parts = node.name.split(".")

        if len(parts) == 1:
            value = self.context[node.name]
        else:
            ctx = self.context
            for part in parts:
                if isinstance(ctx, dict):
                    ctx = ctx[part]
                else:
                    ctx = getattr(ctx, part)
            value = ctx

        for transform in node.transforms:
            func = self.transforms[transform]
            value = func(value)

        if not isinstance(value, str):
            value = str(value)

        self.result += value

    def visit_call(self, node: ast.Call):
        params, macro = self.macros[node.name]
        # macros run in a sub renderer with their own context which is the
        # paramater->arg mapping
        ctx = {}
        for param in params:
            arg = node.arguments[param]
            if isinstance(arg, ast.Lookup):
                arg = self.context[arg.name]
            ctx[param] = arg

        renderer = Renderer(context=ctx, transforms=self.transforms, base=self.base)
        renderer.include_cache = self.include_cache
        renderer.macros = self.macros  # allows recursive macro calls
        macro.accept(renderer)
        self.result += renderer.result


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

    def visit_include(self, node: ast.Include):
        self.depth_log(f"Include({node.source})")

    def visit_macro(self, node: ast.Macro):
        self.depth_log("Macro(")
        self.depth += 1
        self.depth_log(f"name={node.name}")
        self.depth_log(f"parameters={node.parameters}")
        node.body.accept(self)
        self.depth -= 1
        self.depth_log(")")

    def visit_lookup(self, node: ast.Lookup):
        if node.transforms:
            self.depth_log(f"Lookup({node.name} transforms={node.transforms})")
        else:
            self.depth_log(f"Lookup({node.name})")

    def visit_call(self, node: ast.Call):
        self.depth_log("Call(")
        self.depth += 1
        self.depth_log(f"name={node.name}")
        for k, v in node.arguments.items():
            if isinstance(v, ast.Lookup):
                self.depth_log(f"{k}=Lookup({v.name})")
            else:
                self.depth_log(f"{k}={repr(v)}")
        self.depth -= 1
        self.depth_log(")")

    def visit_text(self, node: ast.Text):
        self.depth_log(f"Text({repr(node.text)})")
