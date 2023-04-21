from typing import Any
import rt_preproc.parser.ast as ast
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx

class GraphVizCtx(IVisitorCtx):
    def __init__(self):
        self.nodes = []
        self.edges = []

class GraphVizVisitor(IVisitor):
    """Visitor for printing an AST to a GraphViz dot file."""

    def visit_children(self, node: ast.TreeSitterNode, ctx: GraphVizCtx) -> list[Any]:
        if hasattr(node, "children") and node.children is not None:
            return [child().accept(self, ctx) for child in node.children]
        return []

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: GraphVizCtx) -> Any:
        print(f"TranslationUnit: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.FunctionDefinition, ctx: GraphVizCtx) -> Any:
        print(f"FunctionDefinition: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.FunctionDeclarator, ctx: GraphVizCtx) -> Any:
        print(f"FunctionDeclarator: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.Identifier, ctx: GraphVizCtx) -> Any:
        print(f"Identifier: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ParameterList, ctx: GraphVizCtx) -> Any:
        print(f"ParameterList: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.CompoundStatement, ctx: GraphVizCtx) -> Any:
        print(f"CompoundStatement: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ExpressionStatement, ctx: GraphVizCtx) -> Any:
        print(f"ExpressionStatement: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.CallExpression, ctx: GraphVizCtx) -> Any:
        print(f"CallExpression: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ArgumentList, ctx: GraphVizCtx) -> Any:
        print(f"ArgumentList: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.StringLiteral, ctx: GraphVizCtx) -> Any:
        print(f"StringLiteral: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ReturnStatement, ctx: GraphVizCtx) -> Any:
        print(f"ReturnStatement: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.NumberLiteral, ctx: GraphVizCtx) -> Any:
        print(f"NumberLiteral: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.PrimitiveType, ctx: GraphVizCtx) -> Any:
        print(f"PrimitiveType: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.PreprocInclude, ctx: GraphVizCtx) -> Any:
        print(f"PreprocInclude: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.PreprocIfdef, ctx: GraphVizCtx) -> Any:
        print(f"PreprocIfdef: {node}")
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.SystemLibString, ctx: GraphVizCtx) -> Any:
        print(f"SystemLibString: {node}")
        self.visit_children(node, ctx)

    #
    #   @visit.register@multimethod
    # def visit(self, node: abc.ABCMeta):
    #     print(f"ABC: {node}")
