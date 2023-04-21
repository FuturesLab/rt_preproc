from typing import Any
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from html import escape


class GraphVizCtx(IVisitorCtx):
    def __init__(self, parent: Optional[ast.TreeSitterNode] = None) -> None:
        self.parent = parent


class GraphVizVisitor(IVisitor):
    """Visitor for printing an AST to a GraphViz dot file."""

    def __init__(self) -> None:
        self.buf = ""

    def visit_children(
        self, node: ast.TreeSitterNode, ctx: GraphVizCtx, label: str = None
    ) -> list[Any]:
        def stringize_node(node: ast.TreeSitterNode):
            return f"{node.base_node.id}-{node.base_node.start_point}"

        label = f'"{node.__class__.__name__}"' if label is None else label
        styler = ""
        if node.base_node.type in type_name_to_color:
            styler = f"style=filled color={type_name_to_color[node.base_node.type]}"
        self.buf += f'"{stringize_node(node)}" [{styler} label={label}];\n'
        if ctx.parent is not None:
            self.buf += (
                f'\t"{stringize_node(ctx.parent)}" -> "{stringize_node(node)}";\n'
            )
        if hasattr(node, "children") and node.children is not None:
            self.buf += 'subgraph "cluster_' + stringize_node(node) + '" {\n'
            out = [
                child.accept(self, GraphVizCtx(parent=node)) for child in node.children
            ]
            self.buf += "}\n"
            return out
        return []

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: GraphVizCtx) -> Any:
        self.buf += "digraph Program {\n"
        self.buf += "node [shape=box, colorscheme=pastel19];\n"
        self.visit_children(node, ctx)
        self.buf += "}\n"
        print(self.buf)

    @visit.register
    def visit(self, node: ast.FunctionDefinition, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.FunctionDeclarator, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.Identifier, ctx: GraphVizCtx) -> Any:
        label = (
            "<<TABLE><TR><TD>Identifier</TD></TR><TR><TD>"
            + node.base_node.text.decode("utf8")
            + "</TD></TR></TABLE>>"
        )
        self.visit_children(node, ctx, label=label)

    @visit.register
    def visit(self, node: ast.ParameterList, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.CompoundStatement, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ExpressionStatement, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.CallExpression, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ArgumentList, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.StringLiteral, ctx: GraphVizCtx) -> Any:
        label = (
            "<<TABLE><TR><TD>StringLiteral</TD></TR><TR><TD>"
            + escape(node.base_node.text.decode("utf8"))
            + "</TD></TR></TABLE>>"
        )
        self.visit_children(node, ctx, label=label)

    @visit.register
    def visit(self, node: ast.ReturnStatement, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.NumberLiteral, ctx: GraphVizCtx) -> Any:
        label = (
            "<<TABLE><TR><TD>NumberLiteral</TD></TR><TR><TD>"
            + escape(node.base_node.text.decode("utf8"))
            + "</TD></TR></TABLE>>"
        )
        self.visit_children(node, ctx, label=label)

    @visit.register
    def visit(self, node: ast.PrimitiveType, ctx: GraphVizCtx) -> Any:
        label = (
            "<<TABLE><TR><TD>PrimitiveType</TD></TR><TR><TD>"
            + escape(node.base_node.text.decode("utf8"))
            + "</TD></TR></TABLE>>"
        )
        self.visit_children(node, ctx, label=label)

    @visit.register
    def visit(self, node: ast.PreprocInclude, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.PreprocIfdef, ctx: GraphVizCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.SystemLibString, ctx: GraphVizCtx) -> Any:
        label = (
            "<<TABLE><TR><TD>SystemLibString</TD></TR><TR><TD>"
            + escape(node.base_node.text.decode("utf8"))
            + "</TD></TR></TABLE>>"
        )
        self.visit_children(node, ctx, label=label)

    #
    #   @visit.register@multimethod
    # def visit(self, node: abc.ABCMeta):
    #     print(f"ABC: {node}")


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
    "string_literal": 5,
    "true": 8,
    "type_identifier": 9,
}
