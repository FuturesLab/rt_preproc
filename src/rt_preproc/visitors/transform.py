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
        self.macros: dict[str, str] = {}
        self.buf = ""
        self.seen = []

    def build_setup_prelude(self) -> str:
        buf = ""
        buf += "#include <stdio.h>      /* printf */\n"
        buf += "#include <stdlib.h>     /* strtol */\n"
        buf += "#include <assert.h>     /* assert */\n\n"
        types = set(self.macros[m_name] for m_name in self.macros)

        # TODO: handle non-int data types
        for t in types:
            buf += f"#define UNDEFINED_{t.capitalize()} 0xdeadbeef\n"
        for m_name in self.macros:
            t = self.macros[m_name]
            buf += f"{t} {m_name} = UNDEFINED_{t.capitalize()};\n"

        buf += "\nint setup_env_vars() {\n"
        for m_name in self.macros:
            buf += f'  char* {m_name}_env_str = getenv("FOO");\n'
            buf += f"  if ({m_name}_env_str)"
            # TODO: handle non-int data types
            buf += f" {m_name} = strtol({m_name}_env_str, NULL, 10);\n"

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
        identifier = node.get_named_child(0)
        self.macros[identifier.text] = "int"

        new_node = ast.IfStatement()
        new_node.children = [
            ast.Unnamed("if"),
            ast.Whitespace(" "),
            ast.Unnamed("("),
            node.get_named_child(0),
            ast.Unnamed("!="),
            ast.Identifier("UNDEFINED_Int"),  # TODO: handle types other than int
            ast.Unnamed(")"),
            ast.Whitespace(" "),
            ast.Unnamed("{"),
            ast.Whitespace("\n"),
            node.get_named_child(1),
            ast.Whitespace("\n"),
            ast.Unnamed("}"),
            ast.Whitespace("\n"),
        ]
        # TODO: update children_named_idxs
        return new_node

    @visit.register
    def visit(self, node: ast.FunctionDefinition, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

        func_decl = node.get_named_child(1)
        func_name = func_decl.get_named_child(0).text
        if func_name == "main":
            print("Hey! Found main!")
            setup_env_vars_run_str = r"""
  if (setup_env_vars() != 0) {
    printf("Error setting up environment variables\n");
    return 1;
  }
            """
            body = node.get_named_child(2)
            for i in range(len(body.children)):
                if body.children[i].text == "{":
                    body.children.insert(i + 1, ast.Custom(setup_env_vars_run_str))
                    break
            else:
                raise Exception("No opening brace found in main function body")
            node.set_named_child(2, body)
            return node

    # General expressions...
    @visit.register
    def visit(self, node: ast.AstNode, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
