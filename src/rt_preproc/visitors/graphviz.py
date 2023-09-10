from typing import Any, Union
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from html import escape
import logging

logger = logging.getLogger(__name__)


class GraphVizCtx(IVisitorCtx):
    def __init__(self, parent: Optional[ast.AstNode] = None) -> None:
        self.parent = parent


def stringize_node(node: ast.AstNode):
    if node.base_node is None:
        return f"{node.__class__.__name__}"
    return f"{node.base_node.id}-{node.base_node.start_point}"


def table_label(node: ast.AstNode):
    return (
        "<<TABLE><TR><TD>"
        + node.__class__.__name__
        + "</TD></TR><TR><TD>"
        + escape(node.text)
        + "</TD></TR></TABLE>>"
    )


class GraphVizVisitor(IVisitor):
    """Visitor for printing an AST to a GraphViz dot file."""

    def __init__(self) -> None:
        self.buf = ""

    def visit_named_children(
        self, node: ast.AstNode, ctx: GraphVizCtx, label: str = None
    ) -> list[Any]:
        label = f'"{node.__class__.__name__}"' if label is None else label
        styler = ""
        if node.base_node is not None and node.base_node.type in type_name_to_color:
            styler = f"style=filled color={type_name_to_color[node.base_node.type]}"
        self.buf += f'"{stringize_node(node)}" [{styler} label={label}];\n'
        if ctx.parent is not None:
            self.buf += (
                f'\t"{stringize_node(ctx.parent)}" -> "{stringize_node(node)}";\n'
            )
        self.buf += 'subgraph "cluster_' + stringize_node(node) + '" {\n'
        out = [
            child.accept(self, GraphVizCtx(parent=node))
            for child in node.named_children
        ]
        self.buf += "}\n"
        return out

    @multimethod
    def visit(self, node: ast.AstNode, ctx: GraphVizCtx) -> Any:
        self.visit_named_children(node, ctx)

    @visit.register
    def visit(self, node: ast.TranslationUnit, ctx: GraphVizCtx) -> Any:
        self.buf += "digraph Program {\n"
        self.buf += "node [shape=box, colorscheme=pastel19];\n"
        self.visit_named_children(node, ctx)
        self.buf += "}\n"
        print(self.buf)

    @visit.register
    def visit(
        self,
        node: Union[
            ast.Identifier,
            ast.StringContent,
            ast.NumberLiteral,
            ast.PrimitiveType,
            ast.SystemLibString,
        ],
        ctx: GraphVizCtx,
    ) -> Any:
        self.visit_named_children(node, ctx, label=table_label(node))


type_name_to_color = {
    "preproc_call": 4,
    "preproc_def": 2,
    "preproc_defined": 2,
    "preproc_elif": 2,
    "preproc_else": 2,
    "preproc_function_def": 3,
    "preproc_if": 2,
    "preproc_ifdef": 2,
    "preproc_include": 3,
    "preproc_params": 1,
    "return_statement": 1,
    "identifier": 4,
    "null": 1,
    "number_literal": 5,
    "preproc_arg": 2,
    "preproc_directive": 2,
    "primitive_type": 6,
    "system_lib_string": 7,
    "string_content": 5,
    "true": 8,
    "type_identifier": 9,
}
