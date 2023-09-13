from typing import Any
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx


class TransformCtx(IVisitorCtx):
    def __init__(self, parent: Optional[ast.AstNode] = None) -> None:
        self.parent = parent


class Macro:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type


class TransformVisitor(IVisitor):
    """Visitor for performing variability transformations on AST nodes."""

    def __init__(self) -> None:
        self.macros: list[Macro] = []
        self.buf = ""
        self.seen = []

    def build_setup_prelude(self) -> str:
        buf = ""
        # buf += "#include <stdio.h>      /* printf */\n"
        buf += "#include <stdlib.h>     /* strtol */\n"
        buf += "#include <assert.h>     /* assert */\n\n"
        types = set(m.type for m in self.macros)

        # TODO: handle non-int data types
        for t in types:
            buf += f"#define UNDEFINED_{t.capitalize()} 0xdeadbeef\n"
        for m in self.macros:
            buf += f"{m.type} {m.name} = UNDEFINED_{t.capitalize()};\n"

        buf += "\nint setup_env_vars() {\n"
        for m in self.macros:
            buf += f'  char* {m.name}_env_str = getenv("FOO");\n'
            buf += f"  if ({m.name}_env_str)"
            # TODO: handle non-int data types
            buf += f" {m.name} = strtol({m.name}_env_str, NULL, 10);\n"

        buf += "  return 0;\n"
        buf += "}\n\n"

        return buf

    def visit_children(
        self,
        node: ast.AstNode,
        ctx: TransformCtx,
    ) -> list[Any]:
        for i in range(len(node.children)):
            val = node.children[i].accept(self, TransformCtx(parent=node))
            if val is not None:
                node.children[i] = val

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
        node.children.insert(0, ast.Custom(self.build_setup_prelude()))

    @visit.register
    def visit(self, node: ast.PreprocIfdef, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
        identifier = node.named_children[0]
        # expression = node.named_children[1]
        self.macros.append(Macro(identifier.text, "int"))
        
        new_node = ast.IfStatement()
        new_node.children = [
            ast.Unnamed("if"),
            ast.Whitespace(" "),
            ast.Unnamed("("),
            node.named_children[0],
            ast.Unnamed(")"),
            ast.Whitespace(" "),
            ast.Unnamed("{"),
            ast.Whitespace("\n"),
            node.named_children[1],
            ast.Whitespace("\n"),
            ast.Unnamed("}"),
            ast.Whitespace("\n"),
        ]
        new_node.named_children = node.named_children
        return new_node
        


    # General expressions...
    @visit.register
    def visit(self, node: ast.AstNode, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
